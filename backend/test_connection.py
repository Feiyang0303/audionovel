#!/usr/bin/env python3
"""
Test MongoDB Connection
Simple script to test the MongoDB Atlas connection
"""

import os
from dotenv import load_dotenv

def test_connection():
    """Test MongoDB connection"""
    print("🔍 Testing MongoDB Atlas Connection")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in .env file")
        print("Please run 'python setup_env.py' first")
        return False
    
    print(f"📝 Using connection string: {mongodb_uri[:50]}...")
    
    try:
        from models.database import init_db, get_file_model, get_processing_model
        
        print("🔄 Initializing database connection...")
        
        # Initialize database
        db_instance = init_db()
        
        # Get models
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        print("✅ MongoDB connection successful!")
        print("✅ Database models initialized!")
        
        # Test basic operations
        print("🔄 Testing database operations...")
        
        test_file_data = {
            'filename': 'connection_test.txt',
            'original_filename': 'connection_test.txt',
            'file_path': '/test/path/connection_test.txt',
            'file_size': 256,
            'file_type': 'txt',
            'target_age_group': '8-12'
        }
        
        file_id = file_model.create_file(test_file_data)
        print(f"✅ Test file created with ID: {file_id}")
        
        # Test retrieving the file
        retrieved_file = file_model.get_file_by_id(file_id)
        if retrieved_file:
            print(f"✅ Retrieved file: {retrieved_file['filename']}")
        else:
            print("❌ Failed to retrieve file")
            return False
        
        # Test creating a processing result
        test_result_data = {
            'simplified_text': 'This is a test connection.',
            'characters': [{'name': 'Test', 'dialogue_count': 1}],
            'expert_analyses': {'test': 'Connection test successful'}
        }
        
        result_id = processing_model.create_result(file_id, test_result_data)
        print(f"✅ Created test processing result with ID: {result_id}")
        
        # Test retrieving the processing result
        retrieved_result = processing_model.get_result_by_file_id(file_id)
        if retrieved_result:
            print(f"✅ Retrieved processing result: {retrieved_result['status']}")
        else:
            print("❌ Failed to retrieve processing result")
            return False
        
        # Clean up test data
        print("🔄 Cleaning up test data...")
        from pymongo import MongoClient
        client = MongoClient(mongodb_uri)
        db = client['audionovel']
        db.files.delete_one({'_id': file_id})
        db.processing_results.delete_one({'_id': result_id})
        client.close()
        
        print("✅ Test data cleaned up")
        print("\n🎉 All tests passed! MongoDB is working correctly.")
        
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("1. Check your cluster URL in the .env file")
        print("2. Ensure network access is allowed in Atlas (0.0.0.0/0)")
        print("3. Verify your username and password are correct")
        print("4. Check your internet connection")
        return False

def main():
    """Main function"""
    success = test_connection()
    
    if success:
        print("\n🚀 Ready to start the application!")
        print("Run: python app.py")
    else:
        print("\n❌ Please fix the connection issues before proceeding")

if __name__ == "__main__":
    main() 