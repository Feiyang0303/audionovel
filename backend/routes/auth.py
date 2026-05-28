"""
REST-style auth and user APIs.

- /api/auth/sessions — create (login) / destroy (logout)
- /api/auth/token/validation — optional body token check
- /api/users — register collection
- /api/users/me — current user profile & updates
"""
from flask import Blueprint, request, jsonify
from models.database import get_user_model, get_library_model
from models.user import generate_jwt_token, verify_jwt_token
from middleware.auth import require_auth
from urllib.parse import quote
import re

# ---------------------------------------------------------------------------
# /api/auth/*
# ---------------------------------------------------------------------------
auth_api_bp = Blueprint("auth_api", __name__)


@auth_api_bp.route("/sessions", methods=["POST"])
def create_session():
    """Create session (login) — returns JWT."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if not data.get("email") or not data.get("password"):
            return jsonify({"error": "Email and password are required"}), 400

        email = (data["email"] or "").strip().lower()

        user_model = get_user_model()
        user = user_model.get_user_by_email(email)
        if not user:
            return jsonify({"error": "Invalid email or password"}), 401

        if not user_model.verify_password(user, data["password"]):
            return jsonify({"error": "Invalid email or password"}), 401

        if not user.get("is_active", True):
            return jsonify({"error": "Account is deactivated"}), 401

        token = generate_jwt_token(user["_id"], user.get("email", email))
        user_response = {k: v for k, v in user.items() if k != "password_hash"}

        return jsonify(
            {
                "message": "Login successful",
                "user": user_response,
                "token": token,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@auth_api_bp.route("/sessions", methods=["DELETE"])
def destroy_session():
    """End session (logout). JWT is stateless — client discards token."""
    return "", 204


@auth_api_bp.route("/token/validation", methods=["POST"])
def validate_token():
    """Validate a JWT from JSON body `{ \"token\": \"...\" }`."""
    try:
        data = request.get_json()

        if not data or not data.get("token"):
            return jsonify({"error": "Token is required"}), 400

        payload = verify_jwt_token(data["token"])

        if not payload:
            return jsonify({"error": "Invalid or expired token"}), 401

        user_model = get_user_model()
        user = user_model.get_user_by_id(payload["user_id"])

        if not user:
            return jsonify({"error": "User not found"}), 401

        user_response = {k: v for k, v in user.items() if k != "password_hash"}

        return jsonify({"valid": True, "user": user_response})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------------------------------------------------------
# /api/users/*
# ---------------------------------------------------------------------------
users_bp = Blueprint("users", __name__)


@users_bp.route("", methods=["POST"])
def create_user():
    """Register a new user."""
    try:
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        required_fields = ["username", "email", "password"]
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({"error": f"Missing required field: {field}"}), 400

        data["username"] = (data.get("username") or "").strip()
        data["email"] = (data.get("email") or "").strip().lower()

        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, data["email"]):
            return jsonify({"error": "Invalid email format"}), 400

        if len(data["password"]) < 1:
            return jsonify({"error": "Password cannot be empty"}), 400

        if len(data["username"]) < 1:
            return jsonify({"error": "Username cannot be empty"}), 400

        user_model = get_user_model()

        if user_model.get_user_by_email(data["email"]):
            return jsonify({"error": "Email already registered"}), 409

        if user_model.get_user_by_username(data["username"]):
            return jsonify({"error": "Username already taken"}), 409

        raw_name = data.get("name", data["username"])
        display_name = (raw_name or "").strip() if isinstance(raw_name, str) else str(data["username"])
        if not display_name:
            display_name = data["username"]

        user_data = {
            "username": data["username"],
            "email": data["email"],
            "password": data["password"],
            "name": display_name,
            "profile_pic": data.get(
                "profile_pic",
                f"https://ui-avatars.com/api/?name={quote(display_name)}&background=6366f1&color=fff",
            ),
        }

        user_id = user_model.create_user(user_data)

        user = user_model.get_user_by_id(user_id)
        if user:
            user.pop("password_hash", None)

        token = generate_jwt_token(user_id, data["email"])

        return (
            jsonify(
                {
                    "message": "User registered successfully",
                    "user": user,
                    "token": token,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/me", methods=["GET"])
@require_auth
def get_me():
    """Current user + library stats."""
    try:
        user = request.current_user
        user_response = {k: v for k, v in user.items() if k != "password_hash"}

        library_model = get_library_model()
        library_stats = library_model.get_library_stats(user["_id"])

        return jsonify({"user": user_response, "library_stats": library_stats})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/me", methods=["PATCH"])
@require_auth
def patch_me():
    """Partial update of profile (name, profile_pic)."""
    try:
        user = request.current_user
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        allowed_fields = ["name", "profile_pic"]
        update_data = {k: data[k] for k in allowed_fields if k in data}

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        user_model = get_user_model()
        user_model.update_user(user["_id"], update_data)

        updated_user = user_model.get_user_by_id(user["_id"])
        user_response = {k: v for k, v in updated_user.items() if k != "password_hash"}

        return jsonify(
            {
                "message": "Profile updated successfully",
                "user": user_response,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@users_bp.route("/me/password", methods=["PATCH"])
@require_auth
def patch_me_password():
    """Change password."""
    try:
        user = request.current_user
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        if not data.get("current_password") or not data.get("new_password"):
            return jsonify(
                {"error": "Current password and new password are required"}
            ), 400

        if len(data["new_password"]) < 1:
            return jsonify({"error": "New password cannot be empty"}), 400

        user_model = get_user_model()

        if not user_model.verify_password(user, data["current_password"]):
            return jsonify({"error": "Current password is incorrect"}), 401

        user_model.update_user(user["_id"], {"password": data["new_password"]})

        return jsonify({"message": "Password changed successfully"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

