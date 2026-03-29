from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required

from models.chat_model import ChatModel
from models.profile_model import ProfileModel

from services.chat_service import generate_chat_response
from services.context_service import detect_query_type
from services.news_service import tavily_search_safe

import uuid

chat_bp = Blueprint("chat", __name__)


# ==========================
# 💬 SEND MESSAGE
# ==========================
@chat_bp.route("/send", methods=["POST"])
@token_required
def send_message():
    try:
        data = request.get_json()

        user_id = request.user.get("id")  # ✅ may be None (guest)
        message = data.get("message")
        session_id = data.get("session_id")
        mode = data.get("mode", "normal")

        if not message:
            return jsonify({"error": "Message is required"}), 400

        # ==========================
        # 🆕 CREATE SESSION
        # ==========================
        if not session_id:
            session_id = str(uuid.uuid4())
            print("🆕 NEW SESSION:", session_id)

        # ==========================
        # 👤 GUEST MODE (NO SAVE)
        # ==========================
        if not user_id:
            query_type = detect_query_type(message)

            response = generate_chat_response(
                user_id=None,
                session_id=None,
                user_message=message,
                query_type=query_type
            )

            return jsonify({
                "session_id": None,
                "reply": response
            }), 200

        # ==========================
        # 🧠 NORMAL USER FLOW
        # ==========================
        existing_chat = ChatModel.get_chat_by_session(user_id, session_id)

        if not existing_chat:
            ChatModel.create_chat(user_id, session_id, message)

        # ==========================
        # 🧠 QUERY TYPE
        # ==========================
        query_type = detect_query_type(message)
        ProfileModel.update_query_type(user_id, query_type)

        # ==========================
        # 💾 SAVE USER MESSAGE
        # ==========================
        ChatModel.add_message(user_id, session_id, "user", message)

        # ==========================
        # 🔎 NORMAL MODE (TAVILY + GROQ)
        # ==========================
        if mode == "normal":

            results = tavily_search_safe(message)

            if not results:
                response = generate_chat_response(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=message,
                    query_type="short"
                )

            else:
                results = results[:3]

                context = ""
                for r in results:
                    title = r.get("title", "")
                    url = r.get("url", "")
                    context += f"{title} - {url}\n"

                fast_prompt = f"""
Answer briefly using these search results:

{context}

Question: {message}

Keep answer short.
"""

                response = generate_chat_response(
                    user_id=user_id,
                    session_id=session_id,
                    user_message=fast_prompt,
                    query_type="short"
                )

        # ==========================
        # 🧠 DEEP MODE
        # ==========================
        else:
            enhanced_message = f"""
{message}

Do deep research and provide:
- detailed explanation
- 2 to 3 reference links
"""

            response = generate_chat_response(
                user_id=user_id,
                session_id=session_id,
                user_message=enhanced_message,
                query_type="detailed"
            )

        # ==========================
        # 💾 SAVE BOT MESSAGE
        # ==========================
        ChatModel.add_message(user_id, session_id, "assistant", response)

        return jsonify({
            "session_id": session_id,
            "reply": response
        }), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500


# ==========================
# 📜 GET CHAT HISTORY
# ==========================
@chat_bp.route("/history", methods=["GET"])
@token_required
def get_chat_history():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"chats": []}), 200  # 👤 guest

        chats = ChatModel.get_user_chats(user_id)

        return jsonify({
            "chats": [
                {
                    "session_id": c["session_id"],
                    "title": c.get("title", "New Chat")
                }
                for c in chats
            ]
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# 📂 GET SINGLE CHAT
# ==========================
@chat_bp.route("/<session_id>", methods=["GET"])
@token_required
def get_single_chat(session_id):
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"messages": []}), 200  # 👤 guest

        if not session_id or session_id == "null":
            return jsonify({"messages": []}), 200

        chat = ChatModel.get_chat_by_session(user_id, session_id)

        if not chat:
            return jsonify({"messages": []}), 200

        return jsonify({
            "messages": chat.get("messages", [])
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ❌ DELETE ALL CHATS
# ==========================
@chat_bp.route("/delete-all", methods=["DELETE"])
@token_required
def delete_all_chats():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"message": "Guest mode - nothing to delete"}), 200

        ChatModel.delete_all_chats(user_id)

        return jsonify({
            "message": "All chats deleted"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# ❌ DELETE FIRST CHAT
# ==========================
@chat_bp.route("/delete-last", methods=["DELETE"])
@token_required
def delete_last_chat():
    try:
        user_id = request.user.get("id")

        if not user_id:
            return jsonify({"message": "Guest mode - nothing to delete"}), 200

        result = ChatModel.delete_last_chat(user_id)

        if not result:
            return jsonify({"message": "No chat to delete"}), 200

        return jsonify({
            "message": "First chat deleted"
        }), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500