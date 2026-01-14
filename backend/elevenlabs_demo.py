import os
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs.play import play

load_dotenv()

api_key = os.getenv("ELEVENLABS_API_KEY")
if not api_key:
    raise RuntimeError("Missing ELEVENLABS_API_KEY environment variable. ")

client = ElevenLabs(
  api_key=api_key,
)

audio = client.text_to_dialogue.convert(
    inputs=[
        {
            "text": "[cheerfully] Hello, how are you?",
            "voice_id": "9BWtsMINqrJLrRacOk9x",
        },
        {
            "text": "[stuttering] I'm... I'm doing well, thank you",
            "voice_id": "IKne3meq5aSn9XLyUdCD",
        }
    ]
)

play(audio)
