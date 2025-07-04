#!/usr/bin/env python3
"""
Test script for MongoDB connection and basic operations
"""

import os
from dotenv import load_dotenv
from models.database import init_db, get_file_model, get_processing_model

# Load environment variables
load_dotenv()

def test_mongodb_connection():
    """Test MongoDB connection and basic operations"""
    print("Testing MongoDB connection...")
    
    try:
        # Initialize database
        db_instance = init_db()
        
        # Get models
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        print("✅ MongoDB connection successful!")
        print("✅ Models initialized successfully!")
        
        # Test creating a file
        test_file_data = {
            'filename': 'test_file.txt',
            'original_filename': 'test_file.txt',
            'file_path': '/test/path/test_file.txt',
            'file_size': 1024,
            'file_type': 'txt',
            'target_age_group': '8-12'
        }
        
        file_id = file_model.create_file(test_file_data)
        print(f"✅ Created test file with ID: {file_id}")
        
        # Test retrieving the file
        retrieved_file = file_model.get_file_by_id(file_id)
        if retrieved_file:
            print(f"✅ Retrieved file: {retrieved_file['filename']}")
        else:
            print("❌ Failed to retrieve file")
        
        # Test creating a processing result
        test_result_data = {
            'simplified_text': 'This is a test simplified text.',
            'characters': [{'name': 'Narrator', 'dialogue_count': 1}],
            'expert_analyses': {'test_analyst': 'Test analysis'}
        }
        
        result_id = processing_model.create_result(file_id, test_result_data)
        print(f"✅ Created test processing result with ID: {result_id}")
        
        # Test retrieving the processing result
        retrieved_result = processing_model.get_result_by_file_id(file_id)
        if retrieved_result:
            print(f"✅ Retrieved processing result: {retrieved_result['status']}")
        else:
            print("❌ Failed to retrieve processing result")
        
        # Test getting all files
        all_files = file_model.get_all_files()
        print(f"✅ Retrieved {len(all_files)} files from database")
        
        print("\n🎉 All MongoDB tests passed!")
        
    except Exception as e:
        print(f"❌ MongoDB test failed: {e}")
        print("\nPlease check:")
        print("1. MongoDB is running (local) or connection string is correct (Atlas)")
        print("2. MONGODB_URI environment variable is set (if using Atlas)")
        print("3. Network connection (if using Atlas)")

if __name__ == "__main__":
    test_mongodb_connection() 