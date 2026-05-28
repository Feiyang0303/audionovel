from flask import Blueprint, request, jsonify
from models.database import get_library_model, get_file_model, get_processing_model
from middleware.auth import require_auth

library_bp = Blueprint("library", __name__)


def _enrich_item(item, file_model, processing_model):
    file_data = file_model.get_file_by_id(item["file_id"])
    if file_data:
        item["file"] = file_data
    processing_data = processing_model.get_result_by_file_id(item["file_id"])
    if processing_data:
        item["processing"] = processing_data
    return item


@library_bp.route("/library/items", methods=["GET"])
@require_auth
def list_library_items():
    """
    List current user's library items.
    Query: q (search substring), is_favorite=true|false
    """
    try:
        user = request.current_user
        q = request.args.get("q", "").strip()
        fav_param = request.args.get("is_favorite", "").lower()
        favorite_only = fav_param in ("true", "1", "yes")

        library_model = get_library_model()
        file_model = get_file_model()
        processing_model = get_processing_model()

        library_items = library_model.get_user_library(user["_id"])

        if favorite_only:
            library_items = [
                i for i in library_items if i.get("is_favorite", False)
            ]

        enriched_items = []
        for item in library_items:
            if q:
                file_data = file_model.get_file_by_id(item["file_id"])
                if not file_data:
                    continue
                searchable = (
                    f"{item.get('title', '')} {item.get('description', '')} "
                    f"{file_data.get('original_filename', '')}"
                ).lower()
                if q.lower() not in searchable:
                    continue
                item = _enrich_item(dict(item), file_model, processing_model)
            else:
                item = _enrich_item(dict(item), file_model, processing_model)
            enriched_items.append(item)

        return jsonify({"items": enriched_items, "count": len(enriched_items)})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@library_bp.route("/library/items/<item_id>", methods=["GET"])
@require_auth
def get_library_item(item_id):
    try:
        user = request.current_user
        library_model = get_library_model()
        file_model = get_file_model()
        processing_model = get_processing_model()

        item = library_model.get_library_item(item_id)
        if not item:
            return jsonify({"error": "Library item not found"}), 404

        if item["user_id"] != user["_id"]:
            return jsonify({"error": "Access denied"}), 403

        item = _enrich_item(dict(item), file_model, processing_model)
        return jsonify({"item": item})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@library_bp.route("/library/items", methods=["POST"])
@require_auth
def add_library_item():
    try:
        user = request.current_user
        data = request.get_json()

        if not data or not data.get("file_id"):
            return jsonify({"error": "File ID is required"}), 400

        file_id = str(data["file_id"]).strip()
        file_model = get_file_model()
        file_data = file_model.get_file_by_id(file_id)
        if not file_data:
            return jsonify({"error": "File not found"}), 404

        library_model = get_library_model()
        existing_items = library_model.get_user_library(user["_id"])
        for item in existing_items:
            if item["file_id"] == file_id:
                return jsonify({"error": "File already in library"}), 409

        library_data = {
            "user_id": user["_id"],
            "file_id": file_id,
            "title": data.get("title", file_data["original_filename"]),
            "description": data.get("description", ""),
            "tags": data.get("tags", []),
            "is_favorite": data.get("is_favorite", False),
            "file_type": file_data.get("file_type", ""),
        }

        item_id = library_model.add_to_library(library_data)

        return (
            jsonify(
                {
                    "message": "Added to library successfully",
                    "item_id": item_id,
                }
            ),
            201,
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@library_bp.route("/library/items/<item_id>", methods=["PUT", "PATCH"])
@require_auth
def update_library_item(item_id):
    try:
        user = request.current_user
        data = request.get_json()

        if not data:
            return jsonify({"error": "No data provided"}), 400

        library_model = get_library_model()
        item = library_model.get_library_item(item_id)
        if not item:
            return jsonify({"error": "Library item not found"}), 404

        if item["user_id"] != user["_id"]:
            return jsonify({"error": "Access denied"}), 403

        allowed_fields = ["title", "description", "tags", "is_favorite"]
        update_data = {k: data[k] for k in allowed_fields if k in data}

        if not update_data:
            return jsonify({"error": "No valid fields to update"}), 400

        library_model.update_library_item(item_id, update_data)

        updated = library_model.get_library_item(item_id)
        file_model = get_file_model()
        processing_model = get_processing_model()
        updated = _enrich_item(dict(updated), file_model, processing_model)

        return jsonify(
            {
                "message": "Library item updated successfully",
                "item": updated,
            }
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@library_bp.route("/library/items/<item_id>", methods=["DELETE"])
@require_auth
def remove_library_item(item_id):
    try:
        user = request.current_user
        library_model = get_library_model()

        success = library_model.remove_from_library(item_id, user["_id"])

        if not success:
            return jsonify({"error": "Library item not found or access denied"}), 404

        return "", 204

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@library_bp.route("/library/statistics", methods=["GET"])
@require_auth
def get_library_statistics():
    try:
        user = request.current_user
        library_model = get_library_model()
        stats = library_model.get_library_stats(user["_id"])
        return jsonify({"stats": stats})

    except Exception as e:
        return jsonify({"error": str(e)}), 500
