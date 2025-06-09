from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
from services.text_processor import TextProcessor
from utils import save_uploaded_file, extract_text_from_pdf
from werkzeug.utils import secure_filename

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
# Configure CORS to allow all origins and methods
CORS(app, resources={
    r"/*": {
        "origins": ["http://localhost:5173", "http://localhost:5174"],  # Allow both Vite ports
        "methods": ["GET", "POST", "OPTIONS"],
        "allow_headers": ["Content-Type"]
    }
})

# Initialize the text processor
text_processor = TextProcessor()

# Configuration
UPLOAD_FOLDER = Path("uploads")
AUDIO_OUTPUT_FOLDER = Path("audio_output")
ALLOWED_EXTENSIONS = {'pdf', 'txt', 'epub', 'mobi'}

# Ensure folders exist
UPLOAD_FOLDER.mkdir(exist_ok=True)
AUDIO_OUTPUT_FOLDER.mkdir(exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_OUTPUT_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "message": "Service is running"})

@app.route('/process', methods=['POST'])
def process_text():
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({"error": "No text provided"}), 400

        text = data['text']
        target_age_group = data.get('target_age_group', '8-12')

        # Process the text through all expert roles using Qwen
        result = text_processor.process_text(text, target_age_group)
        
        if result["status"] == "error":
            return jsonify(result), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/upload', methods=['POST'])
def upload_file():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file provided"}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400

        if not allowed_file(file.filename):
            return jsonify({"error": f"Invalid file type. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"}), 400

        # Save the uploaded file
        file_path = save_uploaded_file(file, UPLOAD_FOLDER)
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in {'.epub', '.mobi'}:
            # For now, return error for unsupported formats
            return jsonify({
                "error": f"File type {file_path.suffix} is not yet supported. Please use PDF or TXT files."
            }), 400
        else:
            # For text files, read directly
            text = file_path.read_text()

        # Process the extracted text using Qwen
        target_age_group = request.form.get('target_age_group', '8-12')
        result = text_processor.process_text(text, target_age_group)

        if result["status"] == "error":
            return jsonify(result), 500

        # Return the expected response format
        return jsonify({
            "status": "success",
            "message": "File uploaded and processed successfully",
            "filename": file_path.name,
            "file_path": str(file_path),
            "analysis": result
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)  