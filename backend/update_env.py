#!/usr/bin/env python3
"""
Update .env file with actual MongoDB Atlas connection string
"""

import os
from pathlib import Path

def update_env_file():
    """Update .env file with actual MongoDB Atlas connection string"""
    env_file = Path('.env')
    
    # User's actual MongoDB Atlas connection string
    # Replace <db_password> with the actual password: audio1234
    mongodb_uri = "mongodb+srv://audionovel:audio1234@audionovel.b7cnxeg.mongodb.net/audionovel?retryWrites=true&w=majority&appName=audionovel"
    
    env_content = f"""# MongoDB Configuration
# MongoDB Atlas connection string
MONGODB_URI={mongodb_uri}

# Qwen API Key (for text processing)
QWEN_API_KEY=your_qwen_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_DEBUG=True
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_content)
        print(f"✅ .env file updated at {env_file.absolute()}")
        print("✅ MongoDB Atlas connection string configured:")
        print(f"   Cluster: audionovel.b7cnxeg.mongodb.net")
        print("   Username: audionovel")
        print("   Password: audio1234")
        print("   Database: audionovel")
        return True
    except Exception as e:
        print(f"❌ Failed to update .env file: {e}")
        return False

def main():
    print("🔧 Updating .env file with your MongoDB Atlas connection string...")
    
    if update_env_file():
        print("\n🎉 MongoDB Atlas connection configured successfully!")
        print("\n📝 Next steps:")
        print("1. Run: python test_connection.py")
        print("2. If successful, run: python app.py")
        
        print("\n💡 Your connection string:")
        print("mongodb+srv://audionovel:audio1234@audionovel.b7cnxeg.mongodb.net/audionovel?retryWrites=true&w=majority&appName=audionovel")
    else:
        print("❌ Update failed")

if __name__ == "__main__":
    main() 