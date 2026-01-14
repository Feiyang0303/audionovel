#!/usr/bin/env python3
"""
MongoDB Setup Help
Shows all available commands for MongoDB setup
"""

def main():
    print("🚀 MongoDB Setup Commands for AudioNovel")
    print("=" * 50)
    
    print("\n📋 Available Commands:")
    print("1. python setup_env.py          - Create .env file with your credentials")
    print("2. python get_cluster_url.py    - Get help finding your cluster URL")
    print("3. python test_connection.py    - Test MongoDB connection")
    print("4. python test_mongodb.py       - Run comprehensive MongoDB tests")
    print("5. python app.py                - Start the Flask application")
    
    print("\n🔧 Setup Steps:")
    print("1. Run: python setup_env.py")
    print("2. Run: python get_cluster_url.py")
    print("3. Edit .env file with your actual cluster URL")
    print("4. Run: python test_connection.py")
    print("5. If successful, run: python app.py")
    
    print("\n📝 Your MongoDB Atlas Credentials:")
    print("Username: audionovel")
    print("Password: audio1234")
    print("Database: audionovel")
    
    print("\n🔗 Connection String Format:")
    print("mongodb+srv://audionovel:audio1234@YOUR_CLUSTER_NAME.YOUR_CLUSTER_ID.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    print("\n💡 Tips:")
    print("- Make sure network access is allowed from anywhere (0.0.0.0/0) in Atlas")
    print("- The database 'audionovel' will be created automatically")
    print("- Collections 'files' and 'processing_results' will be created automatically")
    
    print("\n📚 Documentation:")
    print("- README_MONGODB_SETUP.md - Comprehensive setup guide")
    print("- README_MONGODB.md - Original MongoDB documentation")

if __name__ == "__main__":
    main() 