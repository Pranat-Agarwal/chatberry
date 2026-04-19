from datetime import datetime
from config.database import get_db


# ==========================
# 🧠 TITLE GENERATOR
# ==========================
def make_title(message):
    return message[:30] + "..." if len(message) > 30 else message


class ChatModel:

    # ==========================
    # 🆕 CREATE CHAT
    # ==========================
    @staticmethod
    def create_chat(user_id, session_id, first_message):
        if not user_id:
            return  # ❌ guest → don't save

        db = get_db()

        chat = {
            "user_id": user_id,
            "session_id": session_id,
            "title": make_title(first_message),
            "messages": [],
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }

        db.chats.insert_one(chat)

        print("\n=== 🆕 CREATE CHAT ===")
        print("USER_ID:", user_id)
        print("SESSION_ID:", session_id)
        print("TITLE:", make_title(first_message))

    # ==========================
    # 📂 GET CHAT
    # ==========================
    @staticmethod
    def get_chat_by_session(user_id, session_id):
        if not user_id:
            return None  # ❌ guest

        db = get_db()

        return db.chats.find_one({
            "user_id": user_id,
            "session_id": session_id
        })

    # ==========================
    # 💬 ADD MESSAGE
    # ==========================
    @staticmethod
    def add_message(user_id, session_id, role, content):
        if not user_id:
            return  # ❌ guest → don't save

        db = get_db()

        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.utcnow()
        }

        db.chats.update_one(
            {"user_id": user_id, "session_id": session_id},
            {
                "$push": {"messages": message},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True
        )

        print("\n=== 💬 ADD MESSAGE ===")
        print("USER_ID:", user_id)
        print("SESSION_ID:", session_id)
        print("ROLE:", role)
        print("CONTENT:", content[:50])

    # ==========================
    # 📜 GET ALL CHATS
    # ==========================
    @staticmethod
    def get_user_chats(user_id):
        if not user_id:
            return []  # ❌ guest

        db = get_db()

        return list(
            db.chats.find({"user_id": user_id})
            .sort("updated_at", -1)
        )
        print("\n=== 📜 GET USER CHATS ===")
        print("USER_ID:", user_id)

    # ==========================
    # ❌ DELETE FIRST CHAT
    # ==========================
    @staticmethod
    def delete_last_chat(user_id):
        if not user_id:
            return False  # ❌ guest

        db = get_db()

        first_chat = db.chats.find_one(
            {"user_id": user_id},
            sort=[("created_at", 1)]  # 🔥 FIRST ROW
        )

        if not first_chat:
            return False

        db.chats.delete_one({"_id": first_chat["_id"]})

        return True

    # ==========================
    # ❌ DELETE ALL
    # ==========================
    @staticmethod
    def delete_all_chats(user_id):
        if not user_id:
            return  # ❌ guest

        db = get_db()

        return db.chats.delete_many({"user_id": user_id})

    # ==========================
    # 🔄 TO JSON
    # ==========================
    @staticmethod
    def to_json(chat):
        if not chat:
            return None

        return {
            "id": str(chat.get("_id")),
            "user_id": chat.get("user_id"),
            "session_id": chat.get("session_id"),
            "title": chat.get("title", "New Chat"),
            "messages": chat.get("messages", []),
            "created_at": chat.get("created_at"),
            "updated_at": chat.get("updated_at")
        }