#!/usr/bin/env python3
"""
Comprehensive MongoDB Setup Script for AudioNovel
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

def create_env_file():
    """Create .env file with MongoDB configuration"""
    env_file = Path('.env')
    
    if env_file.exists():
        print("✅ .env file already exists")
        return True
    
    print("📄 Creating .env file...")
    
    env_content = """# MongoDB Configuration
# Choose one of the following options:

# Option 1: MongoDB Atlas (Cloud Database) - Recommended
# Get your connection string from MongoDB Atlas dashboard
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority

# Option 2: Local MongoDB
# Uncomment the line below if using local MongoDB
# MONGODB_URI=mongodb://localhost:27017/audionovel

# Qwen API Key (for text processing)
QWEN_API_KEY=your_qwen_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ .env file created successfully!")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def test_mongodb_connection():
    """Test MongoDB connection"""
    print("\n🔍 Testing MongoDB connection...")
    
    try:
        from models.database import init_db, get_file_model, get_processing_model
        
        # Initialize database
        db_instance = init_db()
        
        # Get models
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        print("✅ MongoDB connection successful!")
        print("✅ Database models initialized!")
        
        # Test basic operations
        test_file_data = {
            'filename': 'setup_test.txt',
            'original_filename': 'setup_test.txt',
            'file_path': '/test/path/setup_test.txt',
            'file_size': 512,
            'file_type': 'txt',
            'target_age_group': '8-12'
        }
        
        file_id = file_model.create_file(test_file_data)
        print(f"✅ Test file created with ID: {file_id}")
        
        # Clean up test data
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI', 'mongodb://localhost:27017/'))
        db = client['audionovel']
        db.files.delete_one({'_id': file_id})
        client.close()
        
        print("✅ Test data cleaned up")
        return True
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        return False

def setup_mongodb_atlas():
    """Guide user through MongoDB Atlas setup"""
    print("\n🌐 MongoDB Atlas Setup Guide")
    print("=" * 50)
    
    print("\n📋 Steps to set up MongoDB Atlas:")
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Sign up for a free account")
    print("3. Create a new cluster (choose the free tier)")
    print("4. Click 'Connect' on your cluster")
    print("5. Choose 'Connect your application'")
    print("6. Copy the connection string")
    print("7. Replace <password> with your database password")
    print("8. Replace <dbname> with 'audionovel'")
    
    print("\n📝 Example connection string:")
    print("mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    print("\n🔧 After getting your connection string:")
    print("1. Edit the .env file")
    print("2. Replace the MONGODB_URI with your actual connection string")
    print("3. Run this script again to test the connection")

def setup_local_mongodb():
    """Guide user through local MongoDB setup"""
    print("\n🏠 Local MongoDB Setup Guide")
    print("=" * 50)
    
    print("\n📋 Steps to set up local MongoDB:")
    print("1. Install MongoDB Community Edition:")
    print("   - macOS: brew install mongodb-community")
    print("   - Ubuntu: sudo apt-get install mongodb")
    print("   - Windows: Download from https://www.mongodb.com/try/download/community")
    
    print("\n2. Start MongoDB service:")
    print("   - macOS: brew services start mongodb-community")
    print("   - Ubuntu: sudo systemctl start mongod")
    print("   - Windows: MongoDB runs as a service")
    
    print("\n3. Alternative: Use Docker:")
    print("   docker run -d -p 27017:27017 --name mongodb mongo:latest")
    
    print("\n🔧 Configuration:")
    print("1. Edit the .env file")
    print("2. Uncomment the local MongoDB URI line")
    print("3. Run this script again to test the connection")

def main():
    """Main setup function"""
    print("🚀 AudioNovel MongoDB Setup")
    print("=" * 50)
    
    # Create .env file if it doesn't exist
    if not create_env_file():
        return
    
    # Load environment variables
    load_dotenv()
    
    # Check if MongoDB URI is configured
    mongodb_uri = os.getenv('MONGODB_URI')
    
    if not mongodb_uri or 'username:password' in mongodb_uri:
        print("\n⚠️  MongoDB URI not configured or using default values")
        print("\nChoose your setup option:")
        print("1. MongoDB Atlas (Cloud - Recommended)")
        print("2. Local MongoDB")
        print("3. Exit")
        
        choice = input("\nEnter your choice (1-3): ").strip()
        
        if choice == '1':
            setup_mongodb_atlas()
        elif choice == '2':
            setup_local_mongodb()
        else:
            print("Setup cancelled.")
            return
    else:
        # Test the connection
        if test_mongodb_connection():
            print("\n🎉 MongoDB setup completed successfully!")
            print("\nNext steps:")
            print("1. Run: python app.py")
            print("2. Your application will be available at http://localhost:5001")
        else:
            print("\n❌ MongoDB setup failed!")
            print("Please check your connection string and try again.")

if __name__ == "__main__":
    main() 