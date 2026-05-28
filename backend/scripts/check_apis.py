"""Quick health check for the third-party APIs used by AudioNovel.

Run from the backend directory:
    .venv/bin/python scripts/check_apis.py
"""
from __future__ import annotations

import os
import sys
import traceback
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")


def _section(name: str) -> None:
    print()
    print("=" * 60)
    print(f"  {name}")
    print("=" * 60)


def check_cohere() -> bool:
    _section("Cohere (embeddings)")
    key = os.getenv("COHERE_API_KEY")
    if not key:
        print("FAIL: COHERE_API_KEY not set")
        return False
    print(f"Key present: {key[:6]}...{key[-4:]} (len={len(key)})")

    try:
        import cohere
        print(f"cohere SDK version: {getattr(cohere, '__version__', 'unknown')}")
    except Exception as e:
        print(f"FAIL: cannot import cohere: {e}")
        return False

    # Try the call exactly the way services/cohere_embeddings.py does.
    try:
        client = cohere.Client(key)
        resp = client.embed(
            texts=["Hello from AudioNovel health check."],
            model="embed-english-v3.0",
            input_type="search_document",
            truncate="END",
        )
        emb = resp.embeddings[0]
        print(f"OK: embed-english-v3.0 returned vector of dim={len(emb)}")
        print(f"     first 4 values: {emb[:4]}")
        return True
    except Exception as e:
        print(f"FAIL: Cohere embed call failed: {type(e).__name__}: {e}")
        traceback.print_exc()
        return False


def check_elevenlabs() -> bool:
    _section("ElevenLabs (TTS)")
    key = os.getenv("ELEVENLABS_API_KEY") or os.getenv("ELEVEN_API_KEY")
    if not key:
        print("FAIL: ELEVENLABS_API_KEY not set")
        return False
    print(f"Key present: {key[:6]}...{key[-4:]} (len={len(key)})")

    try:
        from elevenlabs.client import ElevenLabs  # type: ignore
    except Exception as e:
        print(f"FAIL: cannot import elevenlabs: {e}")
        return False

    client = ElevenLabs(api_key=key)

    # The production key is typically restricted to text_to_speech, so user.get()
    # may legitimately 401 with missing_permissions. Note it but don't fail.
    try:
        user = client.user.get()
        sub = getattr(user, "subscription", None)
        tier = getattr(sub, "tier", "unknown") if sub else "unknown"
        used = getattr(sub, "character_count", "?") if sub else "?"
        cap = getattr(sub, "character_limit", "?") if sub else "?"
        print(f"OK: authenticated user (tier={tier}, chars {used}/{cap})")
    except Exception as e:
        print(f"NOTE: user.get() failed (likely restricted key): {type(e).__name__}: {e}")

    # The real check: can we actually synthesize speech?
    voice_id = (
        os.getenv("ELEVENLABS_DEFAULT_VOICE_ID")
        or "JBFqnCBsd6RMkjVDRZzb"  # 'George' - a default ElevenLabs voice
    )
    model_id = os.getenv("ELEVENLABS_MODEL_ID", "eleven_multilingual_v2")
    try:
        chunks = list(client.text_to_speech.convert(
            voice_id,
            text="Hello.",
            model_id=model_id,
            output_format="mp3_44100_128",
        ))
        total = sum(len(c) for c in chunks)
        print(f"OK: TTS convert succeeded (voice={voice_id}, model={model_id}, {total} bytes of mp3)")
        return True
    except Exception as e:
        print(f"FAIL: TTS convert failed: {type(e).__name__}: {e}")
        return False


def check_qwen() -> bool:
    _section("Qwen (text simplification)")
    key = os.getenv("QWEN_API_KEY")
    if not key:
        print("SKIP: QWEN_API_KEY not set in .env (text simplification will fall back to local heuristics).")
        return True  # not a hard failure for this check
    print(f"Key present: {key[:6]}...{key[-4:]} (len={len(key)})")

    import requests
    base_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    headers = {"Authorization": f"Bearer {key}", "Content-Type": "application/json"}
    payload = {
        "model": "qwen-plus",
        "messages": [{"role": "user", "content": "Say 'pong' and nothing else."}],
    }
    try:
        r = requests.post(f"{base_url}/chat/completions", headers=headers, json=payload, timeout=30)
        r.raise_for_status()
        body = r.json()
        msg = body["choices"][0]["message"]["content"]
        print(f"OK: qwen-plus responded: {msg!r}")
        return True
    except Exception as e:
        print(f"FAIL: Qwen request failed: {type(e).__name__}: {e}")
        return False


def main() -> int:
    results = {
        "Cohere":     check_cohere(),
        "ElevenLabs": check_elevenlabs(),
        "Qwen":       check_qwen(),
    }
    _section("Summary")
    for name, ok in results.items():
        print(f"  {name:<12} {'OK' if ok else 'FAIL'}")
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    raise SystemExit(main())
