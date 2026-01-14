#!/usr/bin/env python3
"""
Final MongoDB Test with Unique Filenames
"""

import os
import time
from dotenv import load_dotenv

def test_mongodb():
    """Test MongoDB with unique filenames"""
    print("🔍 Final MongoDB Atlas Test")
    print("=" * 40)
    
    # Load environment variables
    load_dotenv()
    
    # Get MongoDB URI
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri:
        print("❌ MONGODB_URI not found in .env file")
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
        
        # Create unique filename using timestamp
        timestamp = int(time.time())
        unique_filename = f"test_file_{timestamp}.txt"
        
        print(f"🔄 Testing with unique filename: {unique_filename}")
        
        # Test file creation
        test_file_data = {
            'filename': unique_filename,
            'original_filename': unique_filename,
            'file_path': f'/test/path/{unique_filename}',
            'file_size': 256,
            'file_type': 'txt',
            'target_age_group': '8-12'
        }
        
        file_id = file_model.create_file(test_file_data)
        print(f"✅ Test file created with ID: {file_id}")
        
        # Test file retrieval
        retrieved_file = file_model.get_file_by_id(file_id)
        if retrieved_file:
            print(f"✅ Retrieved file: {retrieved_file['filename']}")
        else:
            print("❌ Failed to retrieve file")
            return False
        
        # Test processing result creation
        test_result_data = {
            'simplified_text': f'This is a test for {unique_filename}.',
            'characters': [{'name': 'Test', 'dialogue_count': 1}],
            'expert_analyses': {'test': 'Connection test successful'}
        }
        
        result_id = processing_model.create_result(file_id, test_result_data)
        print(f"✅ Created test processing result with ID: {result_id}")
        
        # Test processing result retrieval
        retrieved_result = processing_model.get_result_by_file_id(file_id)
        if retrieved_result:
            print(f"✅ Retrieved processing result: {retrieved_result['status']}")
        else:
            print("❌ Failed to retrieve processing result")
            return False
        
        # Test getting all files
        all_files = file_model.get_all_files()
        print(f"✅ Total files in database: {len(all_files)}")
        
        # Test getting files by status
        uploaded_files = file_model.get_files_by_status('uploaded')
        print(f"✅ Files with 'uploaded' status: {len(uploaded_files)}")
        
        # Clean up test data
        print("🔄 Cleaning up test data...")
        from pymongo import MongoClient
        client = MongoClient(mongodb_uri)
        db = client['audionovel']
        db.files.delete_one({'_id': file_id})
        db.processing_results.delete_one({'_id': result_id})
        client.close()
        
        print("✅ Test data cleaned up")
        print("\n🎉 All MongoDB tests passed!")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

def test_api_endpoints():
    """Test API endpoints"""
    print("\n🌐 Testing API Endpoints")
    print("=" * 30)
    
    try:
        import requests
        
        # Test health endpoint
        response = requests.get('http://localhost:5001/health')
        if response.status_code == 200:
            print("✅ Health endpoint working")
        else:
            print(f"❌ Health endpoint failed: {response.status_code}")
            return False
        
        # Test files endpoint
        response = requests.get('http://localhost:5001/files')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Files endpoint working - {len(data.get('files', []))} files")
        else:
            print(f"❌ Files endpoint failed: {response.status_code}")
            return False
        
        # Test stats endpoint
        response = requests.get('http://localhost:5001/stats')
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Stats endpoint working - {data.get('files', {}).get('total', 0)} total files")
        else:
            print(f"❌ Stats endpoint failed: {response.status_code}")
            return False
        
        return True
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to Flask app. Is it running?")
        print("   Start it with: python app.py")
        return False
    except Exception as e:
        print(f"❌ API test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 AudioNovel MongoDB & API Test Suite")
    print("=" * 50)
    
    # Test MongoDB
    mongodb_success = test_mongodb()
    
    if mongodb_success:
        print("\n✅ MongoDB is working perfectly!")
        
        # Ask if user wants to test API
        print("\n🌐 Do you want to test the API endpoints?")
        print("   (Make sure the Flask app is running with: python app.py)")
        
        try:
            choice = input("   Test API? (y/n): ").strip().lower()
            if choice == 'y':
                api_success = test_api_endpoints()
                if api_success:
                    print("\n🎉 All tests passed! Your AudioNovel app is ready!")
                else:
                    print("\n⚠️  API tests failed. Check if Flask app is running.")
            else:
                print("\n✅ MongoDB test completed successfully!")
        except KeyboardInterrupt:
            print("\n✅ MongoDB test completed successfully!")
    else:
        print("\n❌ MongoDB test failed. Please check your connection.")

if __name__ == "__main__":
    main() 