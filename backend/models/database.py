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
        # Create indexes for better performance
        self.collection.create_index([("filename", 1)], unique=True)
        self.collection.create_index([("upload_date", -1)])
        self.collection.create_index([("status", 1)])
    
    def create_file(self, file_data: Dict[str, Any]) -> str:
        """Create a new file record"""
        file_data['upload_date'] = datetime.utcnow()
        file_data['status'] = 'uploaded'
        file_data['created_at'] = datetime.utcnow()
        file_data['updated_at'] = datetime.utcnow()
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
            {'$set': {'status': status, 'updated_at': datetime.utcnow()}}
        )
    
    def update_file(self, file_id: str, update_data: Dict[str, Any]):
        """Update file with any data"""
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(file_id)},
            {'$set': update_data}
        )
    
    def delete_file(self, file_id: str) -> bool:
        """Delete a file record"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(file_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_files_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get files by status"""
        files = list(self.collection.find({'status': status}).sort('upload_date', -1))
        for file in files:
            file['_id'] = str(file['_id'])
        return files
    
    def get_files_by_type(self, file_type: str) -> List[Dict[str, Any]]:
        """Get files by file type"""
        files = list(self.collection.find({'file_type': file_type}).sort('upload_date', -1))
        for file in files:
            file['_id'] = str(file['_id'])
        return files
    
    def get_all_files(self) -> List[Dict[str, Any]]:
        """Get all files ordered by upload date"""
        files = list(self.collection.find().sort('upload_date', -1))
        for file in files:
            file['_id'] = str(file['_id'])
        return files
    
    def get_files_count(self) -> int:
        """Get total number of files"""
        return self.collection.count_documents({})
    
    def get_files_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get files uploaded within a date range"""
        files = list(self.collection.find({
            'upload_date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('upload_date', -1))
        for file in files:
            file['_id'] = str(file['_id'])
        return files

class ProcessingResultModel:
    """Model for managing processing results in MongoDB"""
    
    def __init__(self, db):
        self.collection = db['processing_results']
        # Create indexes for better performance
        self.collection.create_index([("file_id", 1)], unique=True)
        self.collection.create_index([("processing_date", -1)])
        self.collection.create_index([("status", 1)])
    
    def create_result(self, file_id: str, result_data: Dict[str, Any]) -> str:
        """Create a new processing result"""
        result_data['file_id'] = file_id
        result_data['processing_date'] = datetime.utcnow()
        result_data['status'] = 'processing'
        result_data['created_at'] = datetime.utcnow()
        result_data['updated_at'] = datetime.utcnow()
        result = self.collection.insert_one(result_data)
        return str(result.inserted_id)
    
    def get_result_by_file_id(self, file_id: str) -> Optional[Dict[str, Any]]:
        """Get processing result by file ID"""
        result = self.collection.find_one({'file_id': file_id})
        if result:
            result['_id'] = str(result['_id'])
        return result
    
    def get_result_by_id(self, result_id: str) -> Optional[Dict[str, Any]]:
        """Get processing result by result ID"""
        try:
            result = self.collection.find_one({'_id': ObjectId(result_id)})
            if result:
                result['_id'] = str(result['_id'])
            return result
        except:
            return None
    
    def update_result(self, result_id: str, update_data: Dict[str, Any]):
        """Update processing result"""
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': update_data}
        )
    
    def update_processing_steps(self, result_id: str, steps: List[Dict[str, Any]]):
        """Update processing steps"""
        self.collection.update_one(
            {'_id': ObjectId(result_id)},
            {'$set': {'processing_steps': steps, 'updated_at': datetime.utcnow()}}
        )
    
    def delete_result(self, result_id: str) -> bool:
        """Delete a processing result"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(result_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_results_by_status(self, status: str) -> List[Dict[str, Any]]:
        """Get results by status"""
        results = list(self.collection.find({'status': status}).sort('processing_date', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def get_all_results(self) -> List[Dict[str, Any]]:
        """Get all processing results ordered by processing date"""
        results = list(self.collection.find().sort('processing_date', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def get_results_count(self) -> int:
        """Get total number of processing results"""
        return self.collection.count_documents({})
    
    def get_results_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Dict[str, Any]]:
        """Get results processed within a date range"""
        results = list(self.collection.find({
            'processing_date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).sort('processing_date', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return results
    
    def get_failed_results(self) -> List[Dict[str, Any]]:
        """Get all failed processing results"""
        results = list(self.collection.find({'status': 'error'}).sort('processing_date', -1))
        for result in results:
            result['_id'] = str(result['_id'])
        return results

# Global database instance
db_instance = None
file_model = None
processing_model = None
user_model = None
library_model = None

def init_db(connection_string: str = None):
    """Initialize the database and models"""
    global db_instance, file_model, processing_model, user_model, library_model
    
    db_instance = MongoDB(connection_string)
    file_model = FileModel(db_instance.db)
    processing_model = ProcessingResultModel(db_instance.db)
    
    # Import and initialize user and library models
    from models.user import UserModel, LibraryModel
    user_model = UserModel(db_instance.db)
    library_model = LibraryModel(db_instance.db)
    
    print("MongoDB models initialized successfully!")
    return db_instance

def get_file_model():
    """Get the file model instance"""
    return file_model

def get_processing_model():
    """Get the processing model instance"""
    return processing_model

def get_user_model():
    """Get the user model instance"""
    return user_model

def get_library_model():
    """Get the library model instance"""
    return library_model

def close_db():
    """Close the database connection"""
    if db_instance:
        db_instance.close()