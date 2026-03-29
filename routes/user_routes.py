from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required

from models.profile_model import ProfileModel

user_bp = Blueprint("user", __name__)


# ==========================
# 👤 GET USER PROFILE
# ==========================
@user_bp.route("/profile", methods=["GET"])
@token_required
def get_profile():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"profile": None}), 200  # 👤 guest

        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return jsonify({"profile": None}), 200

        return jsonify({
            "profile": ProfileModel.to_json(profile)
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 🧠 UPDATE MEMORY
# ==========================
@user_bp.route("/memory", methods=["POST"])
@token_required
def update_memory():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"error": "Login required"}), 401

        data = request.get_json()

        key = data.get("key")
        value = data.get("value")

        if not key or value is None:
            return jsonify({"error": "Key and value required"}), 400

        ProfileModel.update_memory(user_id, key, value)

        return jsonify({
            "message": "Memory updated",
            "key": key,
            "value": value
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 📌 GET MEMORY
# ==========================
@user_bp.route("/memory", methods=["GET"])
@token_required
def get_memory():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"memory": {}}), 200  # 👤 guest

        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return jsonify({"memory": {}}), 200

        return jsonify({
            "memory": profile.get("memory", {})
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ⚙️ UPDATE PREFERENCES
# ==========================
@user_bp.route("/preferences", methods=["POST"])
@token_required
def update_preferences():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"error": "Login required"}), 401

        data = request.get_json()

        if not isinstance(data, dict):
            return jsonify({"error": "Preferences must be JSON"}), 400

        ProfileModel.update_preferences(user_id, data)

        return jsonify({
            "message": "Preferences updated",
            "preferences": data
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 📌 GET PREFERENCES
# ==========================
@user_bp.route("/preferences", methods=["GET"])
@token_required
def get_preferences():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"preferences": {}}), 200  # 👤 guest

        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return jsonify({"preferences": {}}), 200

        return jsonify({
            "preferences": profile.get("preferences", {})
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 🧠 GET QUERY TYPE
# ==========================
@user_bp.route("/query-type", methods=["GET"])
@token_required
def get_query_type():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"query_type": "line"}), 200  # guest default

        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return jsonify({"query_type": "line"}), 200

        return jsonify({
            "query_type": profile.get("last_query_type", "line")
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ❌ CLEAR MEMORY
# ==========================
@user_bp.route("/memory/clear", methods=["DELETE"])
@token_required
def clear_memory():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"error": "Login required"}), 401

        ProfileModel.clear_memory(user_id)

        return jsonify({
            "message": "Memory cleared"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500