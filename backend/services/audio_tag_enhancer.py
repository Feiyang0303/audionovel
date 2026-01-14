import os
from typing import Dict, Any
import requests
from dotenv import load_dotenv

load_dotenv()

QWEN_BASE_URL = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"

# Strict allowlist of voice-only ElevenLabs-style tags
ALLOWED_TAGS = {
    # Directions
    "happy", "sad", "excited", "angry", "whisper", "annoyed", "appalled",
    "thoughtful", "surprised",
    # Non-verbal (voice-only)
    "laughing", "chuckles", "sighs", "clears throat", "short pause",
    "long pause", "exhales sharply", "inhales deeply",
    # Common alternates
    "whispers", "laughs", "crying", "sarcastic", "curious",
}


def _post_chat(api_key: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    response = requests.post(f"{QWEN_BASE_URL}/chat/completions", headers=headers, json=payload)
    response.raise_for_status()
    return response.json()


def enhance_dialogue_with_audio_tags(text: str) -> str:
    """
    Enhance dialogue by adding ElevenLabs v3-style audio tags while strictly preserving original words.
    If QWEN_API_KEY is available, use it; otherwise, return the original text unmodified.
    """
    api_key = os.getenv("QWEN_API_KEY")
    if not api_key:
        return text

    allowed_list = ", ".join(sorted(f"[{t}]" for t in ALLOWED_TAGS))
    system_instructions = (
        "You enhance dialogue text for speech generation by inserting audio tags in square brackets while "
        "strictly preserving the original text and meaning.\n"
        "\nPRIMARY GOAL:\n"
        f"- Add expressive, auditory-only tags chosen ONLY from this allowlist: {allowed_list}\n"
        "- Do not change, add, or delete any words from the original text. Do not place original text in brackets.\n"
        "- Place tags immediately before or after the segment they modify.\n"
        "- Use tags sparingly and contextually. Do not contradict the intent.\n"
        "- Do not introduce non-voice actions (no [walking], [music], [applause], [explosion], etc.). Voice-only.\n"
        "- You may add emphasis via capitalization, an extra question mark, an exclamation mark, or ellipses, "
        "but never alter the original words.\n"
        "\nOUTPUT:\n"
        "- Return ONLY the enhanced dialogue text with inserted tags."
    )

    payload = {
        "model": "qwen-plus",
        "messages": [
            {"role": "system", "content": system_instructions},
            {"role": "user", "content": text},
        ],
    }

    result = _post_chat(api_key, payload)
    content = result["choices"][0]["message"]["content"]

    # Post-filter: remove any tags not in the strict allowlist
    import re
    def _filter_tag(match: "re.Match") -> str:
        raw = match.group(1).strip()
        lowered = raw.lower()
        if lowered in ALLOWED_TAGS:
            # normalize spacing: keep original case and spacing as-is
            return f"[{raw}]"
        return ""  # strip unknown tag

    content = re.sub(r"\[([^\[\]]+)\]", _filter_tag, content)
    return content


