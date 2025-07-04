from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
from services.text_processor import TextProcessor
from utils import save_uploaded_file, extract_text_from_pdf
from werkzeug.utils import secure_filename
from threading import Lock, Thread
from datetime import datetime
import time

# Import MongoDB models
from models.database import init_db, get_file_model, get_processing_model

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

# Initialize MongoDB
init_db()

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

@app.route('/status/<filename>', methods=['GET'])
def get_status(filename):
    try:
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        # Find the uploaded file in database
        uploaded_file = file_model.get_file_by_filename(filename)
        if not uploaded_file:
            return jsonify({"status": "not_found", "message": "No file found with this name."}), 404
        
        # Get processing result
        processing_result = processing_model.get_result_by_file_id(uploaded_file['_id'])
        
        if not processing_result:
            return jsonify({
                "status": "uploaded",
                "message": "File uploaded, processing not started yet."
            })
        
        # Build response with processing steps
        processing_steps = processing_result.get('processing_steps', [])
        
        response = {
            "status": processing_result['status'],
            "processing_steps": processing_steps,
            "processing_date": processing_result['processing_date'].isoformat() if processing_result.get('processing_date') else None
        }
        
        # Add analysis data if completed
        if processing_result['status'] == 'completed' and processing_result.get('simplified_text'):
            response["analysis"] = {
                "simplified_text": processing_result['simplified_text'],
                "characters": processing_result.get('characters', []),
                "expert_analyses": processing_result.get('expert_analyses', {}),
                "target_age_group": uploaded_file.get('target_age_group', '8-12')
            }
        
        return jsonify(response)
        
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
        filename = file_path.name
        file_type = file_path.suffix.lower()[1:]  # Remove the dot
        
        # Extract text based on file type
        if file_path.suffix.lower() == '.pdf':
            text = extract_text_from_pdf(file_path)
        elif file_path.suffix.lower() in {'.epub', '.mobi'}:
            return jsonify({
                "error": f"File type {file_path.suffix} is not yet supported. Please use PDF or TXT files."
            }), 400
        else:
            text = file_path.read_text()

        target_age_group = request.form.get('target_age_group', '8-12')

        # Create database record for uploaded file
        file_model = get_file_model()
        file_data = {
            'filename': filename,
            'original_filename': file.filename,
            'file_path': str(file_path),
            'file_size': file_path.stat().st_size,
            'file_type': file_type,
            'target_age_group': target_age_group
        }
        
        file_id = file_model.create_file(file_data)

        def process_in_background():
            try:
                processing_model = get_processing_model()
                
                # Update file status to processing
                file_model.update_file_status(file_id, 'processing')
                
                # Create processing result record
                result_id = processing_model.create_result(file_id, {})
                
                start_time = time.time()
                processing_steps = []
                
                def progress_callback(step):
                    nonlocal processing_steps
                    processing_steps.append(step.copy())
                    # Update processing steps in database
                    processing_model.update_processing_steps(result_id, processing_steps)
                
                # Process the text
                result = text_processor.process_text(text, target_age_group, progress_callback=progress_callback)
                
                end_time = time.time()
                processing_duration = end_time - start_time
                
                # Update processing result
                update_data = {
                    'simplified_text': result.get('simplified_text', ''),
                    'characters': result.get('characters', []),
                    'expert_analyses': result.get('analysis', {}),
                    'processing_steps': processing_steps,
                    'processing_duration': processing_duration,
                    'status': 'completed' if result.get('status') == 'success' else 'error',
                    'error_message': result.get('message', '') if result.get('status') == 'error' else None
                }
                
                processing_model.update_result(result_id, update_data)
                
                # Update file status
                file_model.update_file_status(file_id, 'completed' if result.get('status') == 'success' else 'error')
                
            except Exception as e:
                # Handle errors
                file_model.update_file_status(file_id, 'error')
                print(f"Error in background processing: {str(e)}")

        # Start background thread
        thread = Thread(target=process_in_background)
        thread.start()

        # Immediately return response so frontend can poll status
        return jsonify({
            "status": "processing",
            "message": "File uploaded and processing started",
            "filename": filename,
            "file_path": str(file_path)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files', methods=['GET'])
def list_files():
    """List all uploaded files"""
    try:
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        files = file_model.get_all_files()
        file_list = []
        
        for file in files:
            file_data = {
                "id": file['_id'],
                "filename": file['filename'],
                "original_filename": file['original_filename'],
                "file_type": file['file_type'],
                "file_size": file['file_size'],
                "upload_date": file['upload_date'].isoformat(),
                "status": file['status'],
                "target_age_group": file.get('target_age_group', '8-12')
            }
            
            # Add processing result info if available
            processing_result = processing_model.get_result_by_file_id(file['_id'])
            if processing_result:
                file_data["processing_result"] = {
                    "status": processing_result['status'],
                    "processing_date": processing_result['processing_date'].isoformat() if processing_result.get('processing_date') else None,
                    "processing_duration": processing_result.get('processing_duration'),
                    "has_simplified_text": bool(processing_result.get('simplified_text'))
                }
            
            file_list.append(file_data)
        
        return jsonify({"files": file_list})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<file_id>', methods=['GET'])
def get_file_details(file_id):
    """Get detailed information about a specific file"""
    try:
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        uploaded_file = file_model.get_file_by_id(file_id)
        if not uploaded_file:
            return jsonify({"error": "File not found"}), 404
        
        file_data = {
            "id": uploaded_file['_id'],
            "filename": uploaded_file['filename'],
            "original_filename": uploaded_file['original_filename'],
            "file_path": uploaded_file['file_path'],
            "file_type": uploaded_file['file_type'],
            "file_size": uploaded_file['file_size'],
            "upload_date": uploaded_file['upload_date'].isoformat(),
            "status": uploaded_file['status'],
            "target_age_group": uploaded_file.get('target_age_group', '8-12')
        }
        
        # Add processing result if available
        processing_result = processing_model.get_result_by_file_id(uploaded_file['_id'])
        if processing_result:
            file_data["processing_result"] = {
                "id": processing_result['_id'],
                "status": processing_result['status'],
                "processing_date": processing_result['processing_date'].isoformat() if processing_result.get('processing_date') else None,
                "processing_duration": processing_result.get('processing_duration'),
                "simplified_text": processing_result.get('simplified_text'),
                "characters": processing_result.get('characters', []),
                "expert_analyses": processing_result.get('expert_analyses', {}),
                "processing_steps": processing_result.get('processing_steps', []),
                "error_message": processing_result.get('error_message')
            }
        
        return jsonify(file_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)  