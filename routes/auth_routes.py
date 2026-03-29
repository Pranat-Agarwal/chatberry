from flask import Blueprint, request, jsonify
from models.user_model import UserModel
from models.profile_model import ProfileModel
from utils.jwt_helper import generate_token

from google.oauth2 import id_token
from google.auth.transport import requests as grequests
from config.config import Config

auth_bp = Blueprint("auth", __name__)


# ==========================
# 🔵 GOOGLE LOGIN ONLY
# ==========================
@auth_bp.route("/google", methods=["POST"])
def google_login():
    try:
        token = request.json.get("token")

        if not token:
            return jsonify({"error": "Token required"}), 400

        # 🔐 Verify Google token
        idinfo = id_token.verify_oauth2_token(
            token,
            grequests.Request(),
            Config.GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        name = idinfo.get("name")

        if not email:
            return jsonify({"error": "Invalid Google token"}), 400

        # ==========================
        # 🔍 CHECK USER
        # ==========================
        user = UserModel.get_user_by_email(email)

        if not user:
            # 👉 AUTO CREATE USER
            user = UserModel.create_user({
                "email": email,
                "name": name,
                "is_verified": True,
                "auth_provider": "google"
            })

            ProfileModel.create_profile(str(user["_id"]))

        # ==========================
        # 🔑 GENERATE TOKEN
        # ==========================
        jwt_token = generate_token(str(user["_id"]))

        return jsonify({
            "message": "Login successful",
            "token": jwt_token,
            "user": UserModel.to_json(user)
        })

    except Exception as e:
        print("❌ GOOGLE LOGIN ERROR:", e)
        return jsonify({"error": str(e)}), 500