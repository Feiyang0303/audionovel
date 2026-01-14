from flask import Blueprint, request, jsonify
from models.database import get_user_model, get_library_model
from models.user import generate_jwt_token
from middleware.auth import require_auth
import re

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['POST'])
def register():
    """Register a new user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        required_fields = ['username', 'email', 'password']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400
        
        # Validate email format
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, data['email']):
            return jsonify({"error": "Invalid email format"}), 400
        
        # Validate password strength (minimum 1 character)
        if len(data['password']) < 1:
            return jsonify({"error": "Password cannot be empty"}), 400
        
        # Validate username format (minimum 1 character, no special restrictions)
        if len(data['username']) < 1:
            return jsonify({"error": "Username cannot be empty"}), 400
        
        user_model = get_user_model()
        
        # Check if email already exists
        existing_user = user_model.get_user_by_email(data['email'])
        if existing_user:
            return jsonify({"error": "Email already registered"}), 409
        
        # Check if username already exists
        existing_username = user_model.get_user_by_username(data['username'])
        if existing_username:
            return jsonify({"error": "Username already taken"}), 409
        
        # Create user
        user_data = {
            'username': data['username'],
            'email': data['email'],
            'password': data['password'],
            'name': data.get('name', data['username']),
            'profile_pic': data.get('profile_pic', f'https://ui-avatars.com/api/?name={data["username"]}&background=6366f1&color=fff')
        }
        
        user_id = user_model.create_user(user_data)
        
        # Get the created user (without password)
        user = user_model.get_user_by_id(user_id)
        if user:
            del user['password_hash']
        
        # Generate JWT token
        token = generate_jwt_token(user_id, data['email'])
        
        return jsonify({
            "message": "User registered successfully",
            "user": user,
            "token": token
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """Login user"""
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Validate required fields
        if not data.get('email') or not data.get('password'):
            return jsonify({"error": "Email and password are required"}), 400
        
        user_model = get_user_model()
        
        # Get user by email
        user = user_model.get_user_by_email(data['email'])
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Verify password
        if not user_model.verify_password(user, data['password']):
            return jsonify({"error": "Invalid email or password"}), 401
        
        # Check if user is active
        if not user.get('is_active', True):
            return jsonify({"error": "Account is deactivated"}), 401
        
        # Generate JWT token
        token = generate_jwt_token(user['_id'], user['email'])
        
        # Remove sensitive data
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            "message": "Login successful",
            "user": user_response,
            "token": token
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['GET'])
@require_auth
def get_profile():
    """Get current user profile"""
    try:
        user = request.current_user
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        # Get library stats
        library_model = get_library_model()
        library_stats = library_model.get_library_stats(user['_id'])
        
        return jsonify({
            "user": user_response,
            "library_stats": library_stats
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/profile', methods=['PUT'])
@require_auth
def update_profile():
    """Update current user profile"""
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        # Fields that can be updated
        allowed_fields = ['name', 'profile_pic']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        user_model = get_user_model()
        user_model.update_user(user['_id'], update_data)
        
        # Get updated user
        updated_user = user_model.get_user_by_id(user['_id'])
        user_response = {k: v for k, v in updated_user.items() if k != 'password_hash'}
        
        return jsonify({
            "message": "Profile updated successfully",
            "user": user_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/change-password', methods=['POST'])
@require_auth
def change_password():
    """Change user password"""
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        if not data.get('current_password') or not data.get('new_password'):
            return jsonify({"error": "Current password and new password are required"}), 400
        
        # Validate new password strength (minimum 1 character)
        if len(data['new_password']) < 1:
            return jsonify({"error": "New password cannot be empty"}), 400
        
        user_model = get_user_model()
        
        # Verify current password
        if not user_model.verify_password(user, data['current_password']):
            return jsonify({"error": "Current password is incorrect"}), 401
        
        # Update password
        user_model.update_user(user['_id'], {'password': data['new_password']})
        
        return jsonify({"message": "Password changed successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        
        if not data or not data.get('token'):
            return jsonify({"error": "Token is required"}), 400
        
        from models.user import verify_jwt_token
        payload = verify_jwt_token(data['token'])
        
        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401
        
        # Get user data
        user_model = get_user_model()
        user = user_model.get_user_by_id(payload['user_id'])
        
        if not user:
            return jsonify({"error": "User not found"}), 401
        
        user_response = {k: v for k, v in user.items() if k != 'password_hash'}
        
        return jsonify({
            "valid": True,
            "user": user_response
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 