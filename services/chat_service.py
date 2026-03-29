from config.groq_client import groq_client
from config.tavily_client import tavily_client

from models.chat_model import ChatModel
from models.profile_model import ProfileModel
from services.memory_service import MemoryService

from config.config import Config


# ==========================
# 🧠 MAIN CHAT FUNCTION
# ==========================
def generate_chat_response(user_id, session_id, user_message, query_type):
    try:
        # ==========================
        # 🧠 DETECT STYLE FROM END
        # ==========================
        user_msg_lower = user_message.lower().strip()

        style = None

        if user_msg_lower.endswith("in points"):
            style = "points"

        elif user_msg_lower.endswith("in paragraph"):
            style = "paragraph"

        elif user_msg_lower.endswith("in short"):
            style = "short"

        elif user_msg_lower.endswith("in detail"):
            style = "detailed"

        elif user_msg_lower.endswith("in one line"):
            style = "one_line"

        elif user_msg_lower.endswith("normal"):
            style = None  # reset

        # ==========================
        # 💾 SAVE STYLE
        # ==========================
        if style is not None and user_id:
            MemoryService.add_memory(user_id, "response_style", style)

        # ==========================
        # ✂️ REMOVE STYLE TEXT FROM MESSAGE
        # ==========================
        if style:
            user_message = user_message.rsplit("in", 1)[0].strip()

        if user_msg_lower.endswith("normal"):
            user_message = user_message.replace("normal", "").strip()

        # ==========================
        # 📜 GET CHAT HISTORY
        # ==========================
        chat = ChatModel.get_chat_by_session(user_id, session_id)

        messages = []

        # ==========================
        # 🧠 SYSTEM PROMPT
        # ==========================
        system_prompt = build_system_prompt(user_id, query_type)

        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # ==========================
        # 📜 ADD HISTORY
        # ==========================
        history_messages = chat.get("messages", [])[-Config.MAX_HISTORY_MESSAGES:] if chat else []

        for msg in history_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # ==========================
        # 🌐 REAL-TIME SEARCH
        # ==========================
        if should_use_search(user_message):
            search_data = tavily_client.search(user_message)
            context = tavily_client.format_results_for_llm(search_data)

            if context:
                messages.append({
                    "role": "system",
                    "content": f"Use this latest information if relevant:\n\n{context}"
                })

        # ==========================
        # 💬 USER MESSAGE
        # ==========================
        messages.append({
            "role": "user",
            "content": user_message
        })

        # ==========================
        # 🤖 AI RESPONSE
        # ==========================
        response = groq_client.generate_response(messages)

        return response

    except Exception as e:
        print(f"❌ Chat Service Error: {str(e)}")
        return "⚠️ Something went wrong while generating response."


# ==========================
# 🧠 SYSTEM PROMPT BUILDER
# ==========================
def build_system_prompt(user_id, query_type):

    profile = ProfileModel.get_profile(user_id)

    memory = profile.get("memory", {}) if profile else {}
    preferences = profile.get("preferences", {}) if profile else {}

    prompt = "You are a highly intelligent AI assistant.\n"

    # ==========================
    # 🧠 USER MEMORY
    # ==========================
    if memory:
        prompt += "\nUser Information:\n"
        for key, value in memory.items():
            if value:
                prompt += f"- {key}: {value}\n"

    # ==========================
    # 🎯 STYLE MEMORY (UPDATED)
    # ==========================
    style = memory.get("response_style")
    if not style:
        style = memory.get("response_style")    

    if style == "points":
        prompt += "\nIMPORTANT: Always respond in bullet points."

    elif style == "paragraph":
        prompt += "\nIMPORTANT: Always respond in paragraph format."

    elif style == "short":
        prompt += "\nIMPORTANT: Keep answers short (2-3 lines)."

    elif style == "detailed":
        prompt += "\nIMPORTANT: Provide detailed explanation with structure."

    elif style == "one_line":
        prompt += "\nIMPORTANT: Respond in only ONE line."

    # ==========================
    # ⚙️ USER PREFERENCES
    # ==========================
    if preferences:
        prompt += "\nUser Preferences:\n"
        for key, value in preferences.items():
            prompt += f"- {key}: {value}\n"

    # ==========================
    # 🎯 QUERY TYPE (SECONDARY)
    # ==========================
    if query_type == "word":
        prompt += "\nRespond in very short (1 line or less)."
    elif query_type == "line":
        prompt += "\nRespond in 2-4 lines clearly."
    else:
        prompt += "\nRespond in detailed explanation with structure."

    # ==========================
    # 🌐 REAL-TIME
    # ==========================
    prompt += "\nIf latest information is provided, prioritize it."

    return prompt


# ==========================
# 🌐 SEARCH DECISION
# ==========================
def should_use_search(user_message):

    keywords = [
        "latest", "today", "news", "current", "recent",
        "price", "stock", "weather", "update", "live", "2026"
    ]

    message_lower = user_message.lower()

    return any(keyword in message_lower for keyword in keywords)