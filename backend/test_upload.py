import requests
import os
from pathlib import Path

def test_file_upload(file_path):
    """Test file upload with a given file"""
    url = 'http://localhost:5001/upload'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f"Error: File {file_path} does not exist")
        return
    
    # Get file extension
    file_ext = Path(file_path).suffix.lower()
    print(f"\nTesting upload of {file_ext} file: {file_path}")
    
    # Prepare the file for upload
    with open(file_path, 'rb') as f:
        files = {'file': (os.path.basename(file_path), f)}
        try:
            # Send POST request
            response = requests.post(url, files=files)
            
            # Print response
            print(f"Status Code: {response.status_code}")
            print("Response:")
            print(response.json())
            
            # If successful, try to download the PDF
            if response.status_code == 200:
                pdf_filename = response.json().get('filename')
                if pdf_filename:
                    download_url = f'http://localhost:5001/files/{pdf_filename}'
                    pdf_response = requests.get(download_url)
                    if pdf_response.status_code == 200:
                        # Save the downloaded PDF
                        output_path = f'test_output_{pdf_filename}'
                        with open(output_path, 'wb') as pdf_file:
                            pdf_file.write(pdf_response.content)
                        print(f"\nSuccessfully downloaded PDF to: {output_path}")
            
        except requests.exceptions.RequestException as e:
            print(f"Error during upload: {str(e)}")

def main():
    # Test the Hamlet file
    hamlet_path = '../test_files/hamlet-002-act-1-scene-1.pdf'
    
    # Test different file types
    test_files = [
        hamlet_path,
    ]
    
    # Run tests
    for file_path in test_files:
        test_file_upload(file_path)

if __name__ == '__main__':
    main() 