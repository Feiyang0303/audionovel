#!/usr/bin/env python3
"""
Quick MongoDB Atlas Setup for AudioNovel
This script helps you set up MongoDB Atlas (cloud database) quickly
"""

import os
import webbrowser
from pathlib import Path
from dotenv import load_dotenv

def main():
    print("🚀 Quick MongoDB Atlas Setup for AudioNovel")
    print("=" * 60)
    
    print("\n📋 This script will help you set up MongoDB Atlas (cloud database)")
    print("MongoDB Atlas provides a free cloud database - perfect for development!")
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"\n✅ .env file found at {env_file.absolute()}")
        load_dotenv()
        mongodb_uri = os.getenv('MONGODB_URI')
        
        if mongodb_uri and 'username:password' not in mongodb_uri:
            print("✅ MongoDB URI is already configured!")
            print(f"Current URI: {mongodb_uri[:50]}...")
            return
        else:
            print("⚠️  MongoDB URI needs to be configured")
    else:
        print(f"\n📄 Creating .env file at {env_file.absolute()}")
    
    print("\n🌐 Setting up MongoDB Atlas:")
    print("1. Opening MongoDB Atlas website...")
    
    # Open MongoDB Atlas in browser
    try:
        webbrowser.open('https://www.mongodb.com/atlas')
        print("✅ Browser opened to MongoDB Atlas")
    except:
        print("⚠️  Could not open browser automatically")
        print("   Please go to: https://www.mongodb.com/atlas")
    
    print("\n📝 Follow these steps:")
    print("1. Sign up for a free MongoDB Atlas account")
    print("2. Create a new cluster (choose the FREE tier)")
    print("3. Click 'Connect' on your cluster")
    print("4. Choose 'Connect your application'")
    print("5. Copy the connection string")
    
    print("\n🔧 Configuration steps:")
    print("1. Replace <password> with your database password")
    print("2. Replace <dbname> with 'audionovel'")
    
    print("\n📝 Example connection string:")
    print("mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    # Create or update .env file
    env_content = """# MongoDB Configuration
# Replace with your actual MongoDB Atlas connection string
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority

# Qwen API Key (for text processing)
QWEN_API_KEY=your_qwen_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"\n✅ .env file created/updated at {env_file.absolute()}")
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return
    
    print("\n🔧 Next steps:")
    print("1. Edit the .env file with your actual MongoDB connection string")
    print("2. Run: python test_mongodb.py")
    print("3. If successful, run: python app.py")
    
    print("\n💡 Tips:")
    print("- Make sure to allow network access from anywhere (0.0.0.0/0) in Atlas")
    print("- Create a database user with read/write permissions")
    print("- The database name 'audionovel' will be created automatically")
    
    print("\n🎯 Ready to test?")
    input("Press Enter when you've updated the .env file with your connection string...")
    
    # Test the connection
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
            'filename': 'atlas_test.txt',
            'original_filename': 'atlas_test.txt',
            'file_path': '/test/path/atlas_test.txt',
            'file_size': 512,
            'file_type': 'txt',
            'target_age_group': '8-12'
        }
        
        file_id = file_model.create_file(test_file_data)
        print(f"✅ Test file created with ID: {file_id}")
        
        # Clean up test data
        from pymongo import MongoClient
        client = MongoClient(os.getenv('MONGODB_URI'))
        db = client['audionovel']
        db.files.delete_one({'_id': file_id})
        client.close()
        
        print("✅ Test data cleaned up")
        print("\n🎉 MongoDB Atlas setup completed successfully!")
        print("\nNext steps:")
        print("1. Run: python app.py")
        print("2. Your application will be available at http://localhost:5001")
        
    except Exception as e:
        print(f"❌ MongoDB connection failed: {e}")
        print("\nPlease check:")
        print("1. Your connection string is correct")
        print("2. Network access is configured in Atlas")
        print("3. Database user has correct permissions")
        print("4. Internet connection is working")

if __name__ == "__main__":
    main() 