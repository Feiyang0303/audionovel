import os
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from services.audio_tag_enhancer import enhance_dialogue_with_audio_tags


def _ensure_audio_folder(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)


def _write_silent_wav(filepath: Path, duration_seconds: float = 1.0) -> None:
    """Create a simple mono 16-bit PCM silent WAV file."""
    import struct
    import wave

    framerate = 22050
    num_channels = 1
    sample_width = 2
    num_frames = int(duration_seconds * framerate)

    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(framerate)
        silence_frame = struct.pack("<h", 0)
        wav_file.writeframes(silence_frame * num_frames)


def get_elevenlabs_api_key() -> Optional[str]:
    return os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_API_KEY")


def default_tts_model_id() -> str:
    return os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")


def default_voice_id_from_env() -> str:
    """Voice ID from the ElevenLabs dashboard (required for restricted keys / script defaults)."""
    return (os.getenv("ELEVENLABS_DEFAULT_VOICE_ID") or "").strip()


def _format_elevenlabs_error(exc: Exception) -> str:
    try:
        from elevenlabs.core.api_error import ApiError  # type: ignore

        if isinstance(exc, ApiError):
            body = exc.body
            if isinstance(body, dict):
                detail = body.get("detail")
                if isinstance(detail, dict) and detail.get("message"):
                    msg = str(detail["message"])
                    code = detail.get("code") or detail.get("status")
                    if code:
                        return f"{msg} (code: {code})"
                    return msg
                if isinstance(detail, str):
                    return detail
            return str(body) if body is not None else str(exc)
    except Exception:
        pass
    return str(exc)


def get_elevenlabs_client():
    from elevenlabs.client import ElevenLabs  # type: ignore

    api_key = get_elevenlabs_api_key()
    if not api_key:
        return None
    return ElevenLabs(api_key=api_key)


def _tts_to_mp3_bytes(client, voice_id: str, text: str, model_id: str) -> bytes:
    chunks: List[bytes] = []
    try:
        for chunk in client.text_to_speech.convert(
            voice_id,
            text=text,
            model_id=model_id,
            output_format="mp3_44100_128",
        ):
            chunks.append(chunk)
    except Exception as e:
        hint = _format_elevenlabs_error(e)
        extra = ""
        if "paid_plan" in hint.lower() or "free users" in hint.lower():
            extra = (
                " Use a voice allowed on your plan (often a voice you created), "
                "or set ELEVENLABS_DEFAULT_VOICE_ID to that voice's ID from the ElevenLabs site."
            )
        elif "voice" in hint.lower() and "not" in hint.lower():
            extra = " Check the voice_id and your API key permissions."
        raise RuntimeError(f"ElevenLabs TTS: {hint}{extra}") from e
    return b"".join(chunks)


def parse_script_lines(script: str) -> List[Tuple[str, str]]:
    """
    Parse lines like 'SPEAKER: dialogue' (same shape as simplified_text from TextProcessor).
    Lines without ':' are treated as NARRATOR.
    """
    segments: List[Tuple[str, str]] = []
    for raw_line in script.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        if ":" not in line:
            segments.append(("NARRATOR", line))
            continue
        speaker, rest = line.split(":", 1)
        speaker = speaker.strip()
        dialogue = rest.strip()
        if not dialogue:
            continue
        segments.append((speaker, dialogue))
    return segments


def _resolve_voice_id(
    speaker: str,
    voice_map: Dict[str, str],
    default_voice_id: str,
) -> str:
    if speaker in voice_map:
        return voice_map[speaker]
    key_upper = speaker.upper()
    if key_upper in voice_map:
        return voice_map[key_upper]
    for k, v in voice_map.items():
        if k.upper() == key_upper:
            return v
    return default_voice_id


def _validate_inputs(inputs: List[Dict]) -> None:
    for i, item in enumerate(inputs):
        if not isinstance(item, dict):
            raise ValueError(f"inputs[{i}] must be an object with text and voice_id")
        text = item.get("text")
        voice_id = item.get("voice_id")
        if not isinstance(text, str) or not text.strip():
            raise ValueError(f"inputs[{i}].text is required and must be non-empty")
        if not isinstance(voice_id, str) or not voice_id.strip():
            raise ValueError(f"inputs[{i}].voice_id is required")


def generate_dialogue_audio(
    inputs: List[Dict],
    *,
    model_id: Optional[str] = None,
    allow_silent_fallback: bool = False,
) -> str:
    """
    Generate dialogue audio from a list of {text, voice_id} items.
    Concatenates MP3 segments (one TTS call per item).

    If no API key and allow_silent_fallback=True, writes a short silent WAV (legacy).
    """
    _validate_inputs(inputs)
    audio_folder = Path("audio_output")
    _ensure_audio_folder(audio_folder)

    mid = (model_id or "").strip() or default_tts_model_id()
    client = get_elevenlabs_client()

    if not client:
        if allow_silent_fallback:
            filename = f"dialogue_{int(time.time())}.wav"
            _write_silent_wav(audio_folder / filename)
            return filename
        raise RuntimeError(
            "ElevenLabs API key missing. Set ELEVENLABS_API_KEY or ELEVEN_API_KEY in your environment."
        )

    parts: List[bytes] = []
    for item in inputs:
        text = item["text"].strip()
        voice_id = item["voice_id"].strip()
        parts.append(_tts_to_mp3_bytes(client, voice_id, text, mid))

    filename = f"dialogue_{int(time.time())}.mp3"
    (audio_folder / filename).write_bytes(b"".join(parts))
    return filename


def generate_script_audio(
    script: str,
    voice_map: Dict[str, str],
    default_voice_id: str,
    *,
    model_id: Optional[str] = None,
    enhance_emotion: bool = False,
) -> str:
    """
    Parse a script (SPEAKER: line per line), map speakers to ElevenLabs voice IDs,
    optionally run Qwen-based audio-tag enhancement per line (requires QWEN_API_KEY).

    Returns MP3 filename under audio_output/.
    """
    script = (script or "").strip()
    if not script:
        raise ValueError("script is empty")

    default_voice_id = default_voice_id.strip() or default_voice_id_from_env()
    if not default_voice_id:
        raise ValueError(
            "default_voice_id is required, or set ELEVENLABS_DEFAULT_VOICE_ID in your environment"
        )

    if not isinstance(voice_map, dict):
        raise ValueError("voice_map must be an object mapping speaker name -> voice_id")

    voice_map = {str(k).strip(): str(v).strip() for k, v in voice_map.items() if str(v).strip()}

    segments = parse_script_lines(script)
    if not segments:
        raise ValueError("no speakable lines found in script")

    inputs: List[Dict] = []
    for speaker, line_text in segments:
        text = line_text
        if enhance_emotion:
            text = enhance_dialogue_with_audio_tags(text)
        voice_id = _resolve_voice_id(speaker, voice_map, default_voice_id)
        inputs.append({"text": text, "voice_id": voice_id})

    return generate_dialogue_audio(inputs, model_id=model_id, allow_silent_fallback=False)
