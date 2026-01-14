from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
from pathlib import Path
from dotenv import load_dotenv
from services.text_processor import TextProcessor
from services.dialogue_generator import generate_dialogue_audio
from services.cohere_embeddings import generate_embedding, search_similar
from services.audio_tag_enhancer import enhance_dialogue_with_audio_tags
from utils import save_uploaded_file, extract_text_from_pdf
from werkzeug.utils import secure_filename
from threading import Lock, Thread
from datetime import datetime
import time

# Import MongoDB models
from models.database import init_db, get_file_model, get_processing_model, get_user_model, get_library_model

# Import authentication and library routes
from routes.auth import auth_bp
from routes.library import library_bp

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# Configure CORS to allow frontend dev server and auth headers
CORS(app, resources={
    r"/*": {
        "origins": [
            "http://localhost:5173",
            "http://localhost:5174",
            "http://127.0.0.1:5173",
            "http://127.0.0.1:5174",
        ],
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
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

# Register blueprints
app.register_blueprint(auth_bp, url_prefix='/auth')
app.register_blueprint(library_bp, url_prefix='/api')

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
                "message": "File uploaded, processing not started yet.",
                "file_id": uploaded_file['_id']
            })
        
        # Build response with processing steps
        processing_steps = processing_result.get('processing_steps', [])
        
        response = {
            "status": processing_result['status'],
            "processing_steps": processing_steps,
            "processing_date": processing_result['processing_date'].isoformat() if processing_result.get('processing_date') else None,
            "file_id": uploaded_file['_id']
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
        
        # Ensure unique filename in DB and on disk
        file_model = get_file_model()
        existing = file_model.get_file_by_filename(filename)
        if existing:
            base = file_path.stem
            suffix = file_path.suffix
            unique_name = f"{base}-{int(time.time())}{suffix}"
            new_path = file_path.with_name(unique_name)
            try:
                file_path.rename(new_path)
                file_path = new_path
                filename = unique_name
            except Exception as e:
                return jsonify({"error": f"Failed to resolve filename conflict: {str(e)}"}), 500
        
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
                
                # Generate embedding for the simplified text (for semantic search)
                simplified_text = result.get('simplified_text', '')
                embedding = None
                if simplified_text:
                    try:
                        embedding = generate_embedding(simplified_text)
                    except Exception as emb_err:
                        print(f"Embedding generation failed: {emb_err}")
                
                # Update processing result
                update_data = {
                    'simplified_text': simplified_text,
                    'characters': result.get('characters', []),
                    'expert_analyses': result.get('analysis', {}),
                    'processing_steps': processing_steps,
                    'processing_duration': processing_duration,
                    'status': 'completed' if result.get('status') == 'success' else 'error',
                    'error_message': result.get('message', '') if result.get('status') == 'error' else None
                }
                if embedding:
                    update_data['embedding'] = embedding
                
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
            "target_age_group": uploaded_file.get('target_age_group', '8-12'),
            "created_at": uploaded_file.get('created_at', uploaded_file['upload_date']).isoformat(),
            "updated_at": uploaded_file.get('updated_at', uploaded_file['upload_date']).isoformat()
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
                "error_message": processing_result.get('error_message'),
                "created_at": processing_result.get('created_at', processing_result['processing_date']).isoformat(),
                "updated_at": processing_result.get('updated_at', processing_result['processing_date']).isoformat()
            }
        
        return jsonify(file_data)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete a file and its processing result"""
    try:
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        # Get file details first
        uploaded_file = file_model.get_file_by_id(file_id)
        if not uploaded_file:
            return jsonify({"error": "File not found"}), 404
        
        # Delete the physical file if it exists
        try:
            file_path = Path(uploaded_file['file_path'])
            if file_path.exists():
                file_path.unlink()
        except Exception as e:
            print(f"Warning: Could not delete physical file: {e}")
        
        # Delete processing result if exists
        processing_result = processing_model.get_result_by_file_id(file_id)
        if processing_result:
            processing_model.delete_result(processing_result['_id'])
        
        # Delete file record
        success = file_model.delete_file(file_id)
        
        if success:
            return jsonify({"message": "File deleted successfully"})
        else:
            return jsonify({"error": "Failed to delete file"}), 500
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/status/<status>', methods=['GET'])
def get_files_by_status(status):
    """Get files by status"""
    try:
        file_model = get_file_model()
        files = file_model.get_files_by_status(status)
        
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
            file_list.append(file_data)
        
        return jsonify({"files": file_list, "count": len(file_list)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/files/type/<file_type>', methods=['GET'])
def get_files_by_type(file_type):
    """Get files by file type"""
    try:
        file_model = get_file_model()
        files = file_model.get_files_by_type(file_type)
        
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
            file_list.append(file_data)
        
        return jsonify({"files": file_list, "count": len(file_list)})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/stats', methods=['GET'])
def get_stats():
    """Get database statistics"""
    try:
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        # Get counts
        total_files = file_model.get_files_count()
        total_results = processing_model.get_results_count()
        
        # Get files by status
        uploaded_files = len(file_model.get_files_by_status('uploaded'))
        processing_files = len(file_model.get_files_by_status('processing'))
        completed_files = len(file_model.get_files_by_status('completed'))
        error_files = len(file_model.get_files_by_status('error'))
        
        # Get results by status
        completed_results = len(processing_model.get_results_by_status('completed'))
        processing_results = len(processing_model.get_results_by_status('processing'))
        error_results = len(processing_model.get_results_by_status('error'))
        
        # Get files by type
        pdf_files = len(file_model.get_files_by_type('pdf'))
        txt_files = len(file_model.get_files_by_type('txt'))
        
        stats = {
            "files": {
                "total": total_files,
                "by_status": {
                    "uploaded": uploaded_files,
                    "processing": processing_files,
                    "completed": completed_files,
                    "error": error_files
                },
                "by_type": {
                    "pdf": pdf_files,
                    "txt": txt_files
                }
            },
            "processing_results": {
                "total": total_results,
                "by_status": {
                    "completed": completed_results,
                    "processing": processing_results,
                    "error": error_results
                }
            }
        }
        
        return jsonify(stats)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/search', methods=['POST'])
def semantic_search():
    """Semantic search across processed scripts using Cohere embeddings.
    
    Expects JSON body: { "query": "search text", "limit": 5 }
    Returns matching processing results with similarity scores.
    """
    try:
        data = request.get_json(silent=True) or {}
        query = data.get('query', '').strip()
        limit = data.get('limit', 5)
        
        if not query:
            return jsonify({"error": "Query is required"}), 400
        
        # Get the processing_results collection directly
        from models.database import db_instance
        if not db_instance:
            return jsonify({"error": "Database not initialized"}), 500
        
        collection = db_instance.db['processing_results']
        
        results = search_similar(query, collection, limit=limit)
        
        # Enrich results with file info
        file_model = get_file_model()
        enriched = []
        for r in results:
            file_data = file_model.get_file_by_id(r.get('file_id'))
            enriched.append({
                "score": r.get('score'),
                "simplified_text": r.get('simplified_text', '')[:500] + '...' if len(r.get('simplified_text', '')) > 500 else r.get('simplified_text', ''),
                "characters": r.get('characters', []),
                "file": {
                    "id": file_data['_id'] if file_data else None,
                    "filename": file_data['filename'] if file_data else None,
                    "original_filename": file_data['original_filename'] if file_data else None
                } if file_data else None
            })
        
        return jsonify({
            "query": query,
            "results": enriched,
            "count": len(enriched)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/save-to-library', methods=['POST'])
def save_to_library():
    """Save a processed file to user's library"""
    try:
        from middleware.auth import require_auth
        from routes.library import add_to_library
        
        # This will be handled by the library blueprint
        return add_to_library()
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dialogue/convert', methods=['POST'])
def dialogue_convert():
    """Convert text inputs to dialogue audio using ElevenLabs.

    Expects JSON body: { "inputs": [ {"text": str, "voice_id": str}, ... ] }
    Returns saved audio filename and URL.
    """
    try:
        data = request.get_json(silent=True) or {}
        inputs = data.get('inputs')
        if not inputs or not isinstance(inputs, list):
            return jsonify({"error": "'inputs' must be a non-empty list of {text, voice_id}"}), 400

        filename = generate_dialogue_audio(inputs)
        return jsonify({
            "message": "Dialogue audio generated",
            "audio_file": filename,
            "url": f"/audio/{filename}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/dialogue/enhance', methods=['POST'])
def dialogue_enhance():
    """Enhance dialogue text by inserting audio tags while preserving original words."""
    try:
        data = request.get_json(silent=True) or {}
        text = data.get('text', '').strip()
        if not text:
            return jsonify({"error": "Field 'text' is required"}), 400
        enhanced = enhance_dialogue_with_audio_tags(text)
        return jsonify({"enhanced_text": enhanced})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001, debug=True)  