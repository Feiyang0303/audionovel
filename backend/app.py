from dotenv import load_dotenv
load_dotenv()
from flask import Flask, request, jsonify, send_from_directory
from utils import simplify_text, generate_audiobook
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
AUDIO_FOLDER = 'audio_output'
ALLOWED_EXTENSIONS = {'pdf', 'txt'}

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)
if not os.path.exists(AUDIO_FOLDER):
    os.makedirs(AUDIO_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return jsonify({"message": "Welcome to the Children's Audiobook System!"})

@app.route('/simplify', methods=['POST'])
def simplify():
    data = request.json
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400

    simplified_story = simplify_text(data["text"])
    return jsonify({"simplified_story": simplified_story})

@app.route('/upload', methods=['POST'])
def upload_book():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        
        return jsonify({
            "message": "File uploaded successfully", 
            "file_path": file_path
        })
    else:
        return jsonify({"error": "Invalid file type"}), 400

@app.route('/generate-audiobook', methods=['POST'])
def create_audiobook():
    data = request.json
    if "text" not in data:
        return jsonify({"error": "No text provided"}), 400
    
    try:
        audio_files = generate_audiobook(data["text"])
        return jsonify({
            "message": "Audiobook generated successfully",
            "audio_files": audio_files
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/audio/<filename>')
def get_audio(filename):
    return send_from_directory(app.config['AUDIO_FOLDER'], filename)

if __name__ == '__main__':
    app.run(port=5001, debug=True)  