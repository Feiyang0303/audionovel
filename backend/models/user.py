from datetime import datetime
from typing import Dict, List, Any, Optional
from bson import ObjectId
import bcrypt
import jwt
import os
from datetime import datetime, timedelta

class UserModel:
    """Model for managing users in MongoDB"""
    
    def __init__(self, db):
        self.collection = db['users']
        # Create indexes for better performance
        self.collection.create_index([("email", 1)], unique=True)
        self.collection.create_index([("username", 1)], unique=True)
        self.collection.create_index([("created_at", -1)])
    
    def create_user(self, user_data: Dict[str, Any]) -> str:
        """Create a new user"""
        # Hash the password
        if 'password' in user_data:
            salt = bcrypt.gensalt()
            user_data['password_hash'] = bcrypt.hashpw(user_data['password'].encode('utf-8'), salt)
            del user_data['password']
        
        user_data['created_at'] = datetime.utcnow()
        user_data['updated_at'] = datetime.utcnow()
        user_data['is_active'] = True
        
        result = self.collection.insert_one(user_data)
        return str(result.inserted_id)
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email"""
        user = self.collection.find_one({'email': email})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def get_user_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username"""
        user = self.collection.find_one({'username': username})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            user = self.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except:
            return None
    
    def verify_password(self, user: Dict[str, Any], password: str) -> bool:
        """Verify user password"""
        if 'password_hash' not in user:
            return False
        return bcrypt.checkpw(password.encode('utf-8'), user['password_hash'])
    
    def update_user(self, user_id: str, update_data: Dict[str, Any]):
        """Update user data"""
        # Handle password update
        if 'password' in update_data:
            salt = bcrypt.gensalt()
            update_data['password_hash'] = bcrypt.hashpw(update_data['password'].encode('utf-8'), salt)
            del update_data['password']
        
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
    
    def delete_user(self, user_id: str) -> bool:
        """Delete a user"""
        try:
            result = self.collection.delete_one({'_id': ObjectId(user_id)})
            return result.deleted_count > 0
        except:
            return False
    
    def get_all_users(self) -> List[Dict[str, Any]]:
        """Get all users"""
        users = list(self.collection.find().sort('created_at', -1))
        for user in users:
            user['_id'] = str(user['_id'])
        return users

class LibraryModel:
    """Model for managing user library items"""
    
    def __init__(self, db):
        self.collection = db['library']
        # Create indexes for better performance
        self.collection.create_index([("user_id", 1)])
        self.collection.create_index([("file_id", 1)])
        self.collection.create_index([("created_at", -1)])
        self.collection.create_index([("user_id", 1), ("created_at", -1)])
    
    def add_to_library(self, library_data: Dict[str, Any]) -> str:
        """Add an item to user's library"""
        library_data['created_at'] = datetime.utcnow()
        library_data['updated_at'] = datetime.utcnow()
        
        result = self.collection.insert_one(library_data)
        return str(result.inserted_id)
    
    def get_user_library(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all items in user's library"""
        items = list(self.collection.find({'user_id': user_id}).sort('created_at', -1))
        for item in items:
            item['_id'] = str(item['_id'])
        return items
    
    def get_library_item(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific library item"""
        try:
            item = self.collection.find_one({'_id': ObjectId(item_id)})
            if item:
                item['_id'] = str(item['_id'])
            return item
        except:
            return None
    
    def remove_from_library(self, item_id: str, user_id: str) -> bool:
        """Remove an item from user's library"""
        try:
            result = self.collection.delete_one({
                '_id': ObjectId(item_id),
                'user_id': user_id
            })
            return result.deleted_count > 0
        except:
            return False
    
    def update_library_item(self, item_id: str, update_data: Dict[str, Any]):
        """Update a library item"""
        update_data['updated_at'] = datetime.utcnow()
        self.collection.update_one(
            {'_id': ObjectId(item_id)},
            {'$set': update_data}
        )
    
    def get_library_stats(self, user_id: str) -> Dict[str, Any]:
        """Get library statistics for a user"""
        total_items = self.collection.count_documents({'user_id': user_id})
        
        # Get items by type
        pdf_items = self.collection.count_documents({'user_id': user_id, 'file_type': 'pdf'})
        txt_items = self.collection.count_documents({'user_id': user_id, 'file_type': 'txt'})
        
        # Get recent items (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        recent_items = self.collection.count_documents({
            'user_id': user_id,
            'created_at': {'$gte': thirty_days_ago}
        })
        
        return {
            'total_items': total_items,
            'pdf_items': pdf_items,
            'txt_items': txt_items,
            'recent_items': recent_items
        }

def generate_jwt_token(user_id: str, email: str) -> str:
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'email': email,
        'exp': datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
        'iat': datetime.utcnow()
    }
    
    secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
    return jwt.encode(payload, secret_key, algorithm='HS256')

def verify_jwt_token(token: str) -> Optional[Dict[str, Any]]:
    """Verify JWT token and return payload"""
    try:
        secret_key = os.getenv('JWT_SECRET_KEY', 'your-secret-key-change-in-production')
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None 