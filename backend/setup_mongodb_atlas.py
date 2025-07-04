#!/usr/bin/env python3
"""
Setup script for MongoDB Atlas configuration
"""

import os
from pathlib import Path

def setup_mongodb_atlas():
    """Guide user through MongoDB Atlas setup"""
    print("🚀 MongoDB Atlas Setup Guide")
    print("=" * 50)
    
    print("\n📋 Steps to set up MongoDB Atlas:")
    print("1. Go to https://www.mongodb.com/atlas")
    print("2. Sign up for a free account")
    print("3. Create a new cluster (choose the free tier)")
    print("4. Click 'Connect' on your cluster")
    print("5. Choose 'Connect your application'")
    print("6. Copy the connection string")
    
    print("\n🔧 Configuration:")
    print("- Replace <password> with your database password")
    print("- Replace <dbname> with 'audionovel'")
    
    print("\n📝 Example connection string:")
    print("mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    # Check if .env file exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"\n✅ .env file already exists at {env_file.absolute()}")
        print("Please add your MONGODB_URI to the existing .env file")
    else:
        print(f"\n📄 Creating .env file at {env_file.absolute()}")
        
        # Create .env file with template
        env_content = """# MongoDB Atlas Connection String
# Replace with your actual connection string from MongoDB Atlas
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/audionovel?retryWrites=true&w=majority

# Qwen API Key (if you have one)
QWEN_API_KEY=your_qwen_api_key_here
"""
        
        with open(env_file, 'w') as f:
            f.write(env_content)
        
        print("✅ .env file created with template")
        print("Please edit the .env file with your actual MongoDB connection string")
    
    print("\n🎯 Next steps:")
    print("1. Edit the .env file with your MongoDB Atlas connection string")
    print("2. Run: python test_mongodb.py")
    print("3. If successful, run: python app.py")
    
    print("\n💡 Alternative: Use Local MongoDB")
    print("If you prefer to use local MongoDB:")
    print("1. Install MongoDB Community Edition")
    print("2. Start MongoDB service")
    print("3. Use connection string: mongodb://localhost:27017/audionovel")

if __name__ == "__main__":
    setup_mongodb_atlas() 