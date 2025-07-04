from pymongo import MongoClient
from datetime import datetime
import os
from typing import Dict, List, Any, Optional
from bson import ObjectId

class MongoDB:
    def __init__(self, connection_string: str = None):
        """Initialize MongoDB connection"""
        if connection_string:
            self.client = MongoClient(connection_string)
        else:
            # Try to get connection string from environment variable
            mongodb_uri = os.getenv('MONGODB_URI')
            if mongodb_uri:
                self.client = MongoClient(mongodb_uri)
            else:
                # Default to local MongoDB
                print("Warning: No MONGODB_URI found in environment. Using local MongoDB.")
                self.client = MongoClient('mongodb://localhost:27017/')
        
        self.db = self.client['audionovel']
        
        # Test the connection
        try:
            self.client.admin.command('ping')
            print("MongoDB connection successful!")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            print("Please check your MongoDB setup and connection string.")
        
    def close(self):
        """Close the database connection"""
        self.client.close()

class FileModel:
    """Model for managing uploaded files in MongoDB"""
    
    def __init__(self, db):
        self.collection = db['files']
    
    def create_file(self, file_data: Dict[str, Any]) -> str:
        """Create a new file record"""
        file_data['upload_date'] = datetime.utcnow()
        file_data['status'] = 'uploaded'
        result = self.collection.insert_one(file_data)
        return str(result.inserted_id)
    
    def get_file_by_filename(self, filename: str) -> Optional[Dict[str, Any]]:
        """Get file by filename"""
        file = self.collection.find_one({'filename': filename})
        if file:
            file['_id'] = str(file['_id'])  # Convert ObjectId to string
        return file
    
    def get_file_by_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get file by ID"""
        try:
            file = self.collection.find_one({'_id': ObjectId(file_id)})
            if file:
                file['_id'] = str(file['_id'])
            return file
        except:
            return None
    
    def update_file_status(self, file_id: str, status: str):
        """Update file status"""
        self.collection.update_one(
            {'_id': ObjectId(file_id)},
            {'$set': {'status': status}}
        )
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all files ordered by upload date"""
        files = list(self.collection.find().sort('upload_date', -1))
        for file in files:
            file['_id'] = str(file['_id'])
        return files

class ProcessingResultModel:
    """Model for managing processing results in MongoDB"""
    
    def __init__(self, db):
        self.collection = db['processing_results']
    
    def create_result(self, file_id: str, result_data: Dict[str, Any]) -> str:
        """Create a new processing result"""
        result_data['file_id'] = file_id
        result_data['processing_date'] = datetime.utcnow()
        result_data['status'] = 'processing'
        result = self.collection.insert_one(result_data)
        return str(result.inserted_id)
    
    def get_result_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get processing result by file ID"""
        result = self.collection.find_one({'file_id': file_id})
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    def update_result(self, result_id: str, update_data: Dict[str, Any]):
        """Update processing result"""
        self.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': update_data}
        )
    
    def update_processing_steps(self, result_id: str, steps: List[Dict[str, Any]]):
        """Update processing steps"""
        self.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': {'processing_steps': steps}}
        )

# Global database instance
db_instance = None
file_model = None
processing_model = None

def init_db(connection_string: str = None):
    """Initialize the database and models"""
    global db_instance, file_model, processing_model
    
    db_instance = MongoDB(connection_string)
    file_model = FileModel(db_instance.db)
    processing_model = ProcessingResultModel(db_instance.db)
    
    print("MongoDB models initialized successfully!")
    return db_instance

def get_file_model():
    """Get the file model instance"""
    return file_model

def get_processing_model():
    """Get the processing model instance"""
    return processing_model

def close_db():
    """Close the database connection"""
    if db_instance:
        db_instance.close()

client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
db = client["audionovel"]
files_collection = db["files"]
results_collection = db["processing_results"]

file_doc = {
    "filename": "test.txt",
    "status": "processing",
    "upload_date": datetime.utcnow(),
    # ...other fields
}
files_collection.insert_one(file_doc)

file = files_collection.find_one({"filename": "test.txt"})
files_collection.update_one({"filename": "test.txt"}, {"$set": {"status": "completed"}}) 