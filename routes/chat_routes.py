from flask import Blueprint, request, jsonify
from middleware.auth_middleware import token_required

from models.chat_model import ChatModel
from models.profile_model import ProfileModel

from services.context_service import detect_query_type
from services.chat_service import generate_chat_response, should_use_search

from config.tavily_client import tavily_client

from services.context_service import enhance_query_with_context

import uuid
import time

chat_bp = Blueprint("chat", __name__)

CACHE = {}
CACHE_TTL = 300  # 5 min


def get_cache(q):
    item = CACHE.get(q)
    if not item:
        return None

    if time.time() - item["time"] > CACHE_TTL:
        return None

    return item["data"]


def set_cache(q, data):
    CACHE[q] = {
        "data": data,
        "time": time.time()
    }


# ==========================
# 💬 SEND MESSAGE
# ==========================
@chat_bp.route("/send", methods=["POST"])
@token_required
def send_message():
    try:
        print("🚀 send_message CALLED")

        user_id, session_id, message, mode, error = handle_user_entry(request)

        if error:
            return jsonify(error), 400

        response = process_chat_logic(user_id, session_id, message, mode)

        # 💾 Save only if logged-in
        if user_id:
            ChatModel.add_message(user_id, session_id, "assistant", response)

        return jsonify({
            "session_id": session_id,
            "reply": response
        }), 200

    except Exception as e:
        print("❌ ERROR:", e)
        return jsonify({"error": str(e)}), 500
    

def handle_user_entry(request):
    data = request.get_json()

    user = getattr(request, "user", None)
    user_id = user.get("id") if user else None

    message = data.get("message")
    session_id = data.get("session_id")
    mode = data.get("mode", "normal")

    if not message:
        return None, None, None, None, {"error": "Message required"}

    # 🆕 Create session
    if not session_id:
        session_id = str(uuid.uuid4())
        print("🆕 NEW SESSION:", session_id)

    print("🚨 USER_ID:", user_id)

    # ==========================
    # 👤 USER FLOW (ONLY IF LOGGED IN)
    # ==========================
    if user_id:
        existing_chat = ChatModel.get_chat_by_session(user_id, session_id)

        if not existing_chat:
            ChatModel.create_chat(user_id, session_id, message)

        query_type = detect_query_type(message)
        ProfileModel.update_query_type(user_id, query_type)

        ChatModel.add_message(user_id, session_id, "user", message)

    return user_id, session_id, message, mode, None


def process_chat_logic(user_id, session_id, message, mode):

    def is_groq_failed(resp):
        r = resp.lower()
        failure_phrases = [
            "i don't have real-time",
            "my knowledge cutoff",
            "i am not aware",
            "i cannot provide",
            "as an ai language model",
            "no current data"
        ]
        return any(p in r for p in failure_phrases)

    # ==========================
    # 🔎 NORMAL MODE
    # ==========================
    if mode == "normal":
        print("🔥 NORMAL MODE")

        results = []

        final_message = message

        # ==========================
        # 🎯 STYLE CHECK
        # ==========================
        msg_lower = message.lower()

        has_style = any(x in msg_lower for x in [
            "in points", "in detail", "in short",
            "in one line", "in paragraph"
        ])

        # get saved style
        saved_style = MemoryService.get_memory(user_id, "response_style") if user_id else None


        if not has_style:
            if saved_style:
                final_message = message + f" in {saved_style.replace('_', ' ')}"
            else:
                final_message = message + " in short"
        else:
            final_message = message
            
        msg_lower = final_message.lower()

        # ==========================
        # 🔍 SEARCH DECISION
        # ==========================
        use_search = should_use_search(message)
        print("USE SEARCH:", use_search)

        cached = get_cache(message)

        # ==========================
        # ⚡ CACHE HIT
        # ==========================
        if cached:
            print("⚡ CACHE HIT")
            results = cached

        # ==========================
        # 🔥 SEARCH CALL
        # ==========================
        elif use_search:
            print("🔥 CALLING SERPER")

            enhanced_query = enhance_query_with_context(message)
            print("🔍 FINAL QUERY:", enhanced_query)

            search_data = tavily_client.search(enhanced_query)

            if search_data and "error" not in search_data:
                results = search_data.get("results", [])

                if results:
                    set_cache(message, results)

        # ==========================
        # ✅ USE SEARCH RESULTS
        # ==========================
        if results:
            context = ""
            for r in results[:3]:   # ✅ limit results
                context += f"{r.get('title')}: {r.get('content')}\n"

            prompt = f"""
    Answer using latest information ONLY from below:

    {context}

    Question: {final_message}
    """

            response = generate_chat_response(
                user_id=user_id,
                session_id=session_id,
                user_message=prompt,
                query_type="short"
            )

        # ==========================
        # 🤖 NO SEARCH → GROQ
        # ==========================
        else:
            response = generate_chat_response(
                user_id=user_id,
                session_id=session_id,
                user_message=final_message,
                query_type="short"
            )

            # ==========================
            # 🔁 FALLBACK → SERPER
            # ==========================
            if is_groq_failed(response):
                print("⚠️ GROQ FAILED → SERPER")

                enhanced_query = enhance_query_with_context(message)

                search_data = tavily_client.search(enhanced_query)

                if search_data and "error" not in search_data:
                    results = search_data.get("results", [])

                    if results:
                        context = ""
                        for r in results[:3]:
                            context += f"{r.get('title')}: {r.get('content')}\n"

                        prompt = f"""
    Answer using latest information ONLY from below:

    {context}

    Question: {final_message}
    """

                        response = generate_chat_response(
                            user_id=user_id,
                            session_id=session_id,
                            user_message=prompt,
                            query_type="short"
                        )

        # ==========================
        # 🎯 FINAL LENGTH CONTROL
        # ==========================
        if "in short" in final_message.lower():
            lines = response.split("\n")
            response = "\n".join(lines[:3])

        elif "in one line" in msg_lower:
            response = response.split("\n")[0]

        return response

    # ==========================
    # 🧠 DEEP MODE
    # ==========================
    else:
        print("🧠 DEEP MODE")

        prompt = f"""
{message}

Give:
- detailed explanation
- references
"""

        response = generate_chat_response(
            user_id=user_id,
            session_id=session_id,
            user_message = prompt + f"\n\nUser preference: {message}",
            query_type="detailed"
        )

    return response


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