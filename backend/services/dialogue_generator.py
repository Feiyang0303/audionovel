import os
import time
from pathlib import Path
from typing import List, Dict


def _ensure_audio_folder(folder: Path) -> None:
    folder.mkdir(parents=True, exist_ok=True)


def _write_silent_wav(filepath: Path, duration_seconds: float = 1.0) -> None:
    """Create a simple mono 16-bit PCM silent WAV file."""
    import wave
    import struct

    framerate = 22050
    num_channels = 1
    sample_width = 2  # bytes (16-bit)
    num_frames = int(duration_seconds * framerate)

    with wave.open(str(filepath), "wb") as wav_file:
        wav_file.setnchannels(num_channels)
        wav_file.setsampwidth(sample_width)
        wav_file.setframerate(framerate)
        # Write silence
        silence_frame = struct.pack("<h", 0)  # 16-bit little-endian zero
        wav_file.writeframes(silence_frame * num_frames)


def _try_generate_with_elevenlabs(inputs: List[Dict], output_path: Path) -> bool:
    """Attempt to generate audio via ElevenLabs SDK. Returns True on success, False on fallback."""
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        return False
    try:
        try:
            from elevenlabs.client import ElevenLabs  # type: ignore
            client = ElevenLabs(api_key=api_key)
            audio_iter = client.text_to_dialogue.convert(inputs=inputs)
            audio_bytes = b"".join(audio_iter)
        except Exception:
            return False

        output_path.write_bytes(audio_bytes)
        return True
    except Exception:
        return False


def generate_dialogue_audio(inputs: List[Dict]) -> str:
    """
    Generate dialogue audio from a list of {text, voice_id} items.
    If ElevenLabs is configured, uses it; otherwise writes a short silent WAV.
    Returns the filename written under audio_output/.
    """
    audio_folder = Path("audio_output")
    _ensure_audio_folder(audio_folder)

    filename = f"dialogue_{int(time.time())}.wav"
    filepath = audio_folder / filename

    if not _try_generate_with_elevenlabs(inputs, filepath):
        _write_silent_wav(filepath, duration_seconds=1.0)

    return filename


