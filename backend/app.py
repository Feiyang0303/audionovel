from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory
from utils import (
    simplify_text, 
    generate_audiobook, 
    save_uploaded_file,
    get_deepseek_client
)
import os
from pathlib import Path
from werkzeug.utils import secure_filename
import PyPDF2

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_output'
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'epub', 'mobi'}

# Ensure folders exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)
Path(AUDIO_FOLDER).mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit


    

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/generate-story', methods=['POST'])
def generate_story():
    data = request.files['file']
    if not data:
        return jsonify({"error": "No file uploaded"}), 400
    
    if not allowed_file(data.filename):
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    print(data)
    result = save_uploaded_file(data)
    pdf_path = result['file_path']
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    simplified_story = simplify_text(text)
    print(simplified_story)
    
    return jsonify({"message": "Story generated successfully"}), 200


@app.route('/simplify', methods=['POST'])
def simplify():
    data = request.files['file']
    if not data:
        return jsonify({"error": "No file uploaded"}), 400
    
    if not allowed_file(data.filename):
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400
    
    simplified_story = simplify_text(data["text"])
    return jsonify({"simplified_story": simplified_story})

@app.route('/upload', methods=['POST'])
def upload_book():
    """Handle file upload and convert to PDF if needed"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        result = save_uploaded_file(file)
        return jsonify({
            "status": "success",
            "message": "File uploaded and converted to PDF successfully",
            "file_path": result['file_path'],
            "filename": result['filename']
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

@app.route('/simplify-pdf', methods=['POST'])
def simplify_pdf():
    """Handle PDF simplification using DeepSeek API"""
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

    try:
        # Save the uploaded file
        result = save_uploaded_file(file)
        pdf_path = result['file_path']

        # Read PDF content
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()

        # Get DeepSeek client and make API request
        client = get_deepseek_client()
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {
                    "role": "system",
                    "content": "Given this PDF of a story, simplify the story"
                },
                {
                    "role": "user",
                    "content": text
                }
            ],
            temperature=0.7,
            max_tokens=2000
        )

        simplified_text = response.choices[0].message.content

        return jsonify({
            "status": "success",
            "simplified_text": simplified_text
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)  