from flask import Blueprint, request, jsonify
from models.database import get_library_model, get_file_model, get_processing_model
from middleware.auth import require_auth, optional_auth
from bson import ObjectId

library_bp = Blueprint('library', __name__)

@library_bp.route('/library', methods=['GET'])
@require_auth
def get_user_library():
    """Get current user's library"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        # Get user's library items
        library_items = library_model.get_user_library(user['_id'])
        
        # Enrich library items with file and processing data
        enriched_items = []
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        for item in library_items:
            # Get file data
            file_data = file_model.get_file_by_id(item['file_id'])
            if file_data:
                item['file'] = file_data
            
            # Get processing result
            processing_data = processing_model.get_result_by_file_id(item['file_id'])
            if processing_data:
                item['processing'] = processing_data
            
            enriched_items.append(item)
        
        return jsonify({
            "library": enriched_items,
            "count": len(enriched_items)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/<item_id>', methods=['GET'])
@require_auth
def get_library_item(item_id):
    """Get a specific library item"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        # Get library item
        item = library_model.get_library_item(item_id)
        if not item:
            return jsonify({"error": "Library item not found"}), 404
        
        # Check if item belongs to user
        if item['user_id'] != user['_id']:
            return jsonify({"error": "Access denied"}), 403
        
        # Enrich with file and processing data
        file_model = get_file_model()
        processing_model = get_processing_model()
        
        file_data = file_model.get_file_by_id(item['file_id'])
        if file_data:
            item['file'] = file_data
        
        processing_data = processing_model.get_result_by_file_id(item['file_id'])
        if processing_data:
            item['processing'] = processing_data
        
        return jsonify({"item": item})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library', methods=['POST'])
@require_auth
def add_to_library():
    """Add a file to user's library"""
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data or not data.get('file_id'):
            return jsonify({"error": "File ID is required"}), 400
        
        file_id = data['file_id']
        
        # Verify file exists
        file_model = get_file_model()
        file_data = file_model.get_file_by_id(file_id)
        if not file_data:
            return jsonify({"error": "File not found"}), 404
        
        library_model = get_library_model()
        
        # Check if already in library
        existing_items = library_model.get_user_library(user['_id'])
        for item in existing_items:
            if item['file_id'] == file_id:
                return jsonify({"error": "File already in library"}), 409
        
        # Add to library
        library_data = {
            'user_id': user['_id'],
            'file_id': file_id,
            'title': data.get('title', file_data['original_filename']),
            'description': data.get('description', ''),
            'tags': data.get('tags', []),
            'is_favorite': data.get('is_favorite', False),
            # Store file_type to support stats and filtering without extra joins
            'file_type': file_data.get('file_type', '')
        }
        
        item_id = library_model.add_to_library(library_data)
        
        return jsonify({
            "message": "Added to library successfully",
            "item_id": item_id
        }), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/<item_id>', methods=['PUT'])
@require_auth
def update_library_item(item_id):
    """Update a library item"""
    try:
        user = request.current_user
        data = request.get_json()
        
        if not data:
            return jsonify({"error": "No data provided"}), 400
        
        library_model = get_library_model()
        
        # Get library item
        item = library_model.get_library_item(item_id)
        if not item:
            return jsonify({"error": "Library item not found"}), 404
        
        # Check if item belongs to user
        if item['user_id'] != user['_id']:
            return jsonify({"error": "Access denied"}), 403
        
        # Fields that can be updated
        allowed_fields = ['title', 'description', 'tags', 'is_favorite']
        update_data = {}
        
        for field in allowed_fields:
            if field in data:
                update_data[field] = data[field]
        
        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400
        
        library_model.update_library_item(item_id, update_data)
        
        return jsonify({"message": "Library item updated successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/<item_id>', methods=['DELETE'])
@require_auth
def remove_from_library(item_id):
    """Remove an item from user's library"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        # Check if item belongs to user and remove it
        success = library_model.remove_from_library(item_id, user['_id'])
        
        if not success:
            return jsonify({"error": "Library item not found or access denied"}), 404
        
        return jsonify({"message": "Removed from library successfully"})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/stats', methods=['GET'])
@require_auth
def get_library_stats():
    """Get user's library statistics"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        stats = library_model.get_library_stats(user['_id'])
        
        return jsonify({"stats": stats})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/search', methods=['GET'])
@require_auth
def search_library():
    """Search user's library"""
    try:
        user = request.current_user
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({"error": "Search query is required"}), 400
        
        library_model = get_library_model()
        file_model = get_file_model()
        
        # Get user's library items
        library_items = library_model.get_user_library(user['_id'])
        
        # Search through library items
        results = []
        for item in library_items:
            # Get file data
            file_data = file_model.get_file_by_id(item['file_id'])
            if not file_data:
                continue
            
            # Search in title, description, and filename
            searchable_text = f"{item.get('title', '')} {item.get('description', '')} {file_data.get('original_filename', '')}".lower()
            
            if query.lower() in searchable_text:
                item['file'] = file_data
                results.append(item)
        
        return jsonify({
            "results": results,
            "count": len(results),
            "query": query
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/favorites', methods=['GET'])
@require_auth
def get_favorites():
    """Get user's favorite library items"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        # Get all library items
        library_items = library_model.get_user_library(user['_id'])
        
        # Filter favorites
        favorites = [item for item in library_items if item.get('is_favorite', False)]
        
        # Enrich with file data
        file_model = get_file_model()
        for item in favorites:
            file_data = file_model.get_file_by_id(item['file_id'])
            if file_data:
                item['file'] = file_data
        
        return jsonify({
            "favorites": favorites,
            "count": len(favorites)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@library_bp.route('/library/<item_id>/favorite', methods=['POST'])
@require_auth
def toggle_favorite(item_id):
    """Toggle favorite status of a library item"""
    try:
        user = request.current_user
        library_model = get_library_model()
        
        # Get library item
        item = library_model.get_library_item(item_id)
        if not item:
            return jsonify({"error": "Library item not found"}), 404
        
        # Check if item belongs to user
        if item['user_id'] != user['_id']:
            return jsonify({"error": "Access denied"}), 403
        
        # Toggle favorite status
        new_favorite_status = not item.get('is_favorite', False)
        library_model.update_library_item(item_id, {'is_favorite': new_favorite_status})
        
        return jsonify({
            "message": f"{'Added to' if new_favorite_status else 'Removed from'} favorites",
            "is_favorite": new_favorite_status
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500 