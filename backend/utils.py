import os
from pathlib import Path
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader

def save_uploaded_file(file, upload_folder: Path) -> Path:
    """
    Save an uploaded file and return its path.
    """
    filename = secure_filename(file.filename)
    file_path = upload_folder / filename
    file.save(file_path)
    return file_path

def extract_text_from_pdf(file_path: Path) -> str:
    """
    Extract text from a PDF file.
    """
    text = ""
    with open(file_path, 'rb') as pdf_file:
        pdf_reader = PdfReader(pdf_file)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text