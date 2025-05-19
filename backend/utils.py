from openai import OpenAI
import os
import tempfile
import time
from pathlib import Path
from dotenv import load_dotenv
from werkzeug.utils import secure_filename
import ebooklib
from ebooklib import epub
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import mobi
import requests

load_dotenv()

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
def convert_to_pdf(file_path):
    file_path = Path(file_path)
    file_ext = file_path.suffix.lower()
    output_path = file_path.with_suffix('.pdf')

    if file_ext == '.pdf':
        return str(file_path)

    text = ""

    if file_ext == '.txt':
        text = file_path.read_text(encoding='utf-8')

    elif file_ext == '.epub':
        book = epub.read_epub(str(file_path))
        text = '\n'.join([item.get_content().decode('utf-8') 
                          for item in book.get_items_of_type(ebooklib.ITEM_DOCUMENT)])

    elif file_ext == '.mobi':
        tempdir, filepath = mobi.extract(str(file_path))
        text = Path(filepath).read_text(encoding='utf-8')
        mobi.cleanup(tempdir)
    
    else:
        raise ValueError(f"Unsupported file format: {file_ext}")

    # Write to PDF 
    c = canvas.Canvas(str(output_path), pagesize=letter)
    width, height = letter
    y = height - 40 

    for line in text.split('\n'):
        if y < 40:
            c.showPage()
            y = height - 40
        c.drawString(40, y, line.strip())
        y -= 14

    c.save()

    return str(output_path)

def save_uploaded_file(file):
    """Save uploaded file and convert to PDF if needed"""
    upload_dir = Path('uploads')
    upload_dir.mkdir(exist_ok=True)
    
    # Handle Unicode filenames
    filename = secure_filename(file.filename)
    if not filename:  # If secure_filename returns empty
        filename = f"upload_{int(time.time())}{Path(file.filename).suffix}"
    
    # Save original file
    original_path = upload_dir / filename
    file.save(original_path)
    
    # Convert to PDF if needed
    pdf_path = original_path
    if Path(original_path).suffix.lower() != '.pdf':
        try:
            pdf_path = convert_to_pdf(original_path)
            # Remove original file if conversion was successful
            original_path.unlink()
        except Exception as e:
            # If conversion fails, keep original file and raise error
            raise Exception(f"Failed to convert file to PDF: {str(e)}")
    
    return {
        'file_path': str(pdf_path),
        'filename': Path(pdf_path).name,
        'is_pdf': True
    }

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