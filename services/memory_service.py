from models.profile_model import ProfileModel


class MemoryService:

    # ==========================
    # 🧠 GET USER MEMORY
    # ==========================
    @staticmethod
    def get_memory(user_id):
        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return {}

        return profile.get("memory", {})

    # ==========================
    # ➕ ADD / UPDATE MEMORY
    # ==========================
    @staticmethod
    def add_memory(user_id, key, value):
        """
        Store user-specific information
        Example:
        name, goal, preference, etc.
        """
        ProfileModel.update_memory(user_id, key, value)

        return {
            "message": "Memory stored successfully",
            "key": key,
            "value": value
        }

    # ==========================
    # ❌ DELETE MEMORY KEY
    # ==========================
    @staticmethod
    def delete_memory_key(user_id, key):
        profile = ProfileModel.get_profile(user_id)

        if not profile:
            return {"error": "Profile not found"}

        memory = profile.get("memory", {})

        if key in memory:
            del memory[key]

            ProfileModel.update_preferences(user_id, {
                **profile.get("preferences", {}),
            })

            ProfileModel.update_memory(user_id, key, None)

        return {
            "message": f"Memory key '{key}' deleted"
        }

    # ==========================
    # ❌ CLEAR ALL MEMORY
    # ==========================
    @staticmethod
    def clear_memory(user_id):
        ProfileModel.clear_memory(user_id)   # ✅ correct

        return {
            "message": "All memory cleared"
        }
        

    # ==========================
    # 🧠 FORMAT MEMORY FOR AI
    # ==========================
    @staticmethod
    def format_memory_for_prompt(user_id):
        """
        Convert memory into LLM-friendly format
        """

        memory = MemoryService.get_memory(user_id)

        if not memory:
            return ""

        formatted = "User Known Information:\n"

        for key, value in memory.items():
            if value:
                formatted += f"- {key}: {value}\n"

        return formatted.strip()