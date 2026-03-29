from datetime import datetime
from config.database import get_profile_collection


class ProfileModel:

    # ==========================
    # 🆕 CREATE PROFILE
    # ==========================
    @staticmethod
    def create_profile(user_id):
        if not user_id:
            return  # ❌ guest safety

        profiles = get_profile_collection()

        profile = {
            "user_id": user_id,
            "preferences": {},
            "memory": {},
            "last_query_type": "line",
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        profiles.insert_one(profile)
        return profile

    # ==========================
    # 📂 GET PROFILE
    # ==========================
    @staticmethod
    def get_profile(user_id):
        if not user_id:
            return None  # ❌ guest

        profiles = get_profile_collection()
        return profiles.find_one({"user_id": user_id})

    # ==========================
    # 🧠 UPDATE MEMORY
    # ==========================
    @staticmethod
    def update_memory(user_id, key, value):
        if not user_id:
            return  # ❌ guest

        profiles = get_profile_collection()

        return profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    f"memory.{key}": value,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    # ==========================
    # ❌ CLEAR MEMORY (FIXED)
    # ==========================
    @staticmethod
    def clear_memory(user_id):
        if not user_id:
            return

        profiles = get_profile_collection()

        return profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "memory": {},
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    # ==========================
    # ⚙️ UPDATE PREFERENCES
    # ==========================
    @staticmethod
    def update_preferences(user_id, preferences: dict):
        if not user_id:
            return

        profiles = get_profile_collection()

        return profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "preferences": preferences,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    # ==========================
    # 🧠 UPDATE QUERY TYPE
    # ==========================
    @staticmethod
    def update_query_type(user_id, query_type):
        if not user_id:
            return

        profiles = get_profile_collection()

        return profiles.update_one(
            {"user_id": user_id},
            {
                "$set": {
                    "last_query_type": query_type,
                    "updated_at": datetime.utcnow()
                }
            },
            upsert=True
        )

    # ==========================
    # ❌ DELETE PROFILE
    # ==========================
    @staticmethod
    def delete_profile(user_id):
        if not user_id:
            return

        profiles = get_profile_collection()
        return profiles.delete_one({"user_id": user_id})

    # ==========================
    # 🔄 TO JSON
    # ==========================
    @staticmethod
    def to_json(profile):
        if not profile:
            return None

        return {
            "user_id": profile.get("user_id"),
            "preferences": profile.get("preferences", {}),
            "memory": profile.get("memory", {}),
            "last_query_type": profile.get("last_query_type", "line"),
            "created_at": profile.get("created_at")
        }