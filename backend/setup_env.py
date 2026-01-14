#!/usr/bin/env python3
"""
Setup .env file with MongoDB Atlas credentials
"""

import os
from pathlib import Path

def create_env_file():
    """Create .env file with MongoDB Atlas credentials"""
    env_file = Path('.env')
    
    # MongoDB Atlas connection string with user's credentials
    env_content = """# MongoDB Configuration
# MongoDB Atlas connection string
MONGODB_URI=mongodb+srv://audionovel:audio1234@cluster0.mongodb.net/audionovel?retryWrites=true&w=majority

# Qwen API Key (for text processing)
QWEN_API_KEY=your_qwen_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ .env file created at {env_file.absolute()}")
        print("✅ MongoDB Atlas credentials configured:")
        print("   Username: audionovel")
        print("   Password: audio1234")
        print("   Database: audionovel")
        return True
    except Exception as e:
        print(f"❌ Failed to create .env file: {e}")
        return False

def main():
    print("🔧 Setting up .env file with MongoDB Atlas credentials...")
    
    if create_env_file():
        print("\n📝 Next steps:")
        print("1. Update the MONGODB_URI with your actual cluster URL")
        print("2. Replace 'cluster0.mongodb.net' with your actual cluster address")
        print("3. Run: python test_mongodb.py")
        print("4. If successful, run: python app.py")
        
        print("\n💡 Note: You'll need to update the cluster URL in the .env file")
        print("   The current URI uses 'cluster0.mongodb.net' as a placeholder")
        print("   Replace it with your actual cluster address from MongoDB Atlas")
    else:
        print("❌ Setup failed")

if __name__ == "__main__":
    main() 