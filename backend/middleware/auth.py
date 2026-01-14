from functools import wraps
from flask import request, jsonify
from models.user import verify_jwt_token
from models.database import get_user_model

def require_auth(f):
    """Decorator to require authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if not auth_header:
            return jsonify({"error": "Authorization header missing"}), 401
        
        # Check if it's a Bearer token
        if not auth_header.startswith('Bearer '):
            return jsonify({"error": "Invalid authorization header format"}), 401
        
        token = auth_header.split(' ')[1]
        
        # Verify token
        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get user from database
        user_model = get_user_model()
        user = user_model.get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        if not user.get('is_active', True):
            return jsonify({"error": "User account is deactivated"}), 401
        
        # Add user to request context
        request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function

def optional_auth(f):
    """Decorator for optional authentication"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Get token from Authorization header
        auth_header = request.headers.get('Authorization')
        
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            
            # Verify token
            payload = verify_jwt_token(token)
            if payload:
                # Get user from database
                user_model = get_user_model()
                user = user_model.get_user_by_id(payload['user_id'])
                
                if user and user.get('is_active', True):
                    # Add user to request context
                    request.current_user = user
        
        return f(*args, **kwargs)
    
    return decorated_function 