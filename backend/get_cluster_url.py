#!/usr/bin/env python3
"""
Get MongoDB Atlas Cluster URL
This script helps you find your actual cluster URL from MongoDB Atlas
"""

import webbrowser
import os
from pathlib import Path

def main():
    print("🔍 Getting MongoDB Atlas Cluster URL")
    print("=" * 50)
    
    print("\n📋 To find your cluster URL, follow these steps:")
    print("1. Opening MongoDB Atlas dashboard...")
    
    try:
        webbrowser.open('https://cloud.mongodb.com')
        print("✅ Browser opened to MongoDB Atlas")
    except:
        print("⚠️  Could not open browser automatically")
        print("   Please go to: https://cloud.mongodb.com")
    
    print("\n📝 Steps to find your cluster URL:")
    print("1. Sign in to MongoDB Atlas")
    print("2. Click on your cluster name")
    print("3. Click the 'Connect' button")
    print("4. Choose 'Connect your application'")
    print("5. Copy the connection string")
    
    print("\n🔧 Your connection string should look like this:")
    print("mongodb+srv://audionovel:audio1234@YOUR_CLUSTER_NAME.YOUR_CLUSTER_ID.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    print("\n📝 Replace these parts:")
    print("- YOUR_CLUSTER_NAME: Your actual cluster name")
    print("- YOUR_CLUSTER_ID: Your actual cluster ID")
    
    print("\n💡 Example:")
    print("mongodb+srv://audionovel:audio1234@cluster0.abc123.mongodb.net/audionovel?retryWrites=true&w=majority")
    
    print("\n🎯 Once you have your cluster URL:")
    print("1. Edit the .env file")
    print("2. Replace the MONGODB_URI with your actual connection string")
    print("3. Run: python test_mongodb.py")
    
    # Check if .env exists
    env_file = Path('.env')
    if env_file.exists():
        print(f"\n✅ .env file found at {env_file.absolute()}")
        print("You can edit it with any text editor to update the cluster URL")
    else:
        print(f"\n❌ .env file not found. Run 'python setup_env.py' first")

if __name__ == "__main__":
    main() 