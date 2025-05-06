from openai import OpenAI
import os
import requests
from pathlib import Path

openai_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY')) 

def get_deepseek_client():
    client = OpenAI(
        api_key=os.getenv('DEEPSEEK_API_KEY'),
        base_url="https://api.deepseek.com/v1",
        default_headers = {
        "User-Agent": "ChildrensAudiobook/1.0",
        "Accept-Encoding": "gzip, deflate"
        }
    )
    return client

def simplify_text(text, max_retries=3):
    for attempt in range(max_retries):
        try:
            client = get_deepseek_client()
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {
                        "role": "system",
                        "content": "Simplify this story for children aged 5-10. Keep characters and main plot points."
                    },
                    {
                        "role": "user",
                        "content": text
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == max_retries - 1:
                raise  # Final attempt, propagate error
            continue  # Will retry

# Unchanged OpenAI TTS function (works perfectly)
def generate_character_voice(text, character, output_path):
    """Generate voice using OpenAI TTS (unchanged)"""
    voice_mapping = {
        "NARRATOR": "nova",
        "default": "alloy"
    }
    voice = voice_mapping.get(character, voice_mapping["default"])
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    response = openai_client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=text,
        speed=1.0  # Normal speed for children's content
    )
    response.stream_to_file(output_path)

# Improved audiobook generator
def generate_audiobook(text, output_dir="audio_output"):
    """Generates and returns all audio files with better error handling"""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    try:
        simplified_text = simplify_text(text)
        lines = [line.strip() for line in simplified_text.split('\n') if line.strip()]
        audio_files = []
        
        for i, line in enumerate(lines):
            if ':' in line:
                character, dialogue = line.split(':', 1)
                character = character.strip().upper()
                dialogue = dialogue.strip()
            else:
                character = "NARRATOR"
                dialogue = line
                
            output_path = str(Path(output_dir) / f"line_{i}_{character}.mp3")
            generate_character_voice(dialogue, character, output_path)
            audio_files.append(output_path)
            
        return {
            "status": "success",
            "simplified_text": simplified_text,
            "audio_files": audio_files
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }