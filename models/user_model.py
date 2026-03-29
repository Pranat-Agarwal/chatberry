from datetime import datetime
from bson import ObjectId
from config.database import get_users_collection


class UserModel:

    # ==========================
    # 🆕 CREATE USER (GOOGLE)
    # ==========================
    @staticmethod
    def create_user(data):
        users = get_users_collection()

        user = {
            "email": data.get("email"),
            "name": data.get("name"),
            "auth_provider": data.get("auth_provider", "google"),
            "created_at": datetime.utcnow()
        }

        result = users.insert_one(user)
        user["_id"] = str(result.inserted_id)

        return user

    # ==========================
    # 🔍 GET USER BY EMAIL
    # ==========================
    @staticmethod
    def get_user_by_email(email):
        users = get_users_collection()
        return users.find_one({"email": email})

    # ==========================
    # 🔍 GET USER BY ID
    # ==========================
    @staticmethod
    def get_user_by_id(user_id):
        users = get_users_collection()
        return users.find_one({"_id": ObjectId(user_id)})

    # ==========================
    # ❌ DELETE USER
    # ==========================
    @staticmethod
    def delete_user(user_id):
        users = get_users_collection()
        return users.delete_one({"_id": ObjectId(user_id)})

    # ==========================
    # 🔄 TO JSON
    # ==========================
    @staticmethod
    def to_json(user):
        if not user:
            return None

        return {
            "id": str(user["_id"]),
            "email": user.get("email"),
            "name": user.get("name"),
            "auth_provider": user.get("auth_provider"),
            "created_at": user.get("created_at")
        }