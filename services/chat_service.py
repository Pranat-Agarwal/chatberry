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
        user_msg_lower = user_message.lower().strip()
        style = None

        # ==========================
        # 🧠 STYLE MAP
        # ==========================
        style_map = {
            "in points": "points",
            "in paragraph": "paragraph",
            "in short": "short",
            "in detail": "detailed",
            "in one line": "one_line",
            "normal": None
        }

        # ==========================
        # 🧠 GET SAVED STYLE
        # ==========================
        saved_style = None
        if user_id:
            memory = MemoryService.get_memory(user_id)
            saved_style = memory.get("response_style")

        # ==========================
        # 🧠 DETECT STYLE FROM QUERY
        # ==========================
        for key, value in style_map.items():
            if key in user_msg_lower:
                style = value
                break

        # ==========================
        # 🧠 FALLBACK TO SAVED STYLE
        # ==========================
        if style is None and saved_style:
            style = saved_style
            print("🧠 USING SAVED STYLE:", style)

        print("🎯 FINAL STYLE:", style)

        # ==========================
        # 💾 SAVE STYLE ONLY IF USER EXPLICITLY SETS
        # ==========================
        if any(k in user_msg_lower for k in style_map.keys()) and user_id:
            MemoryService.add_memory(user_id, "response_style", style)

        # ==========================
        # ✂️ REMOVE STYLE TEXT SAFELY
        # ==========================
        for phrase in style_map.keys():
            if user_msg_lower.endswith(phrase):
                user_message = user_message[: -len(phrase)].strip()
                break

        # ==========================
        # 📜 GET CHAT HISTORY
        # ==========================
        chat = ChatModel.get_chat_by_session(user_id, session_id)

        messages = []

        # ==========================
        # 🧠 SYSTEM PROMPT
        # ==========================
        system_prompt = build_system_prompt(user_id, query_type)

        # 🔥 STRONG STYLE ENFORCEMENT
        if style == "points":
            system_prompt += "\nIMPORTANT: Answer ONLY in bullet points."
        elif style == "paragraph":
            system_prompt += "\nIMPORTANT: Answer ONLY in paragraph."
        elif style == "short":
            system_prompt += "\nIMPORTANT: Answer in 2-3 lines only."
        elif style == "detailed":
            system_prompt += "\nIMPORTANT: Provide detailed structured explanation."
        elif style == "one_line":
            system_prompt += "\nIMPORTANT: Answer in EXACTLY ONE short line."

        messages.append({
            "role": "system",
            "content": system_prompt
        })

        # ==========================
        # 📜 HISTORY
        # ==========================
        history_messages = chat.get("messages", [])[-Config.MAX_HISTORY_MESSAGES:] if chat else []

        for msg in history_messages:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # ==========================
        # 💬 USER MESSAGE (FORCE STYLE)
        # ==========================
        style_instruction = ""

        if style == "points":
            style_instruction = "Answer ONLY in bullet points."
        elif style == "paragraph":
            style_instruction = "Answer in paragraph."
        elif style == "short":
            style_instruction = "Answer in MAX 2-3 lines."
        elif style == "detailed":
            style_instruction = "Give detailed explanation."
        elif style == "one_line":
            style_instruction = "Answer in ONE SHORT LINE ONLY."

        messages.append({
            "role": "user",
            "content": f"{user_message}\n\n{style_instruction}"
        })

        # ==========================
        # 🤖 AI RESPONSE
        # ==========================
        max_tokens = 50 if style in ["short", "one_line"] else 500

        response = groq_client.generate_response(
            messages,
            max_tokens=max_tokens
        )

        # ==========================
        # 🎯 FINAL HARD CONTROL
        # ==========================
        if style == "one_line":
            response = response.split("\n")[0]

        elif style == "short":
            response = "\n".join(response.split("\n")[:3])

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
            if key != "response_style" and value:
                prompt += f"- {key}: {value}\n"

    # ==========================
    # 🎯 STYLE MEMORY (PRIMARY CONTROL)
    # ==========================
    style = memory.get("response_style")

    if style == "points":
        prompt += "\nIMPORTANT: Respond ONLY in bullet points."

    elif style == "paragraph":
        prompt += "\nIMPORTANT: Respond ONLY in paragraph format."

    elif style == "short":
        prompt += "\nIMPORTANT: Respond in MAX 2-3 lines."

    elif style == "detailed":
        prompt += "\nIMPORTANT: Provide detailed structured explanation."

    elif style == "one_line":
        prompt += "\nIMPORTANT: Respond in EXACTLY ONE short line."

    # ==========================
    # ⚙️ USER PREFERENCES
    # ==========================
    if preferences:
        prompt += "\nUser Preferences:\n"
        for key, value in preferences.items():
            prompt += f"- {key}: {value}\n"

    # ==========================
    # 🎯 QUERY TYPE (SECONDARY ONLY)
    # ==========================
    # 👉 apply ONLY if no style is set
    if not style:
        if query_type == "word":
            prompt += "\nRespond in very short (1 line or less)."

        elif query_type == "line":
            prompt += "\nRespond in 2-4 lines clearly."

        else:
            prompt += "\nRespond in 2-3 lines only."

    # ==========================
    # 🌐 REAL-TIME PRIORITY
    # ==========================
    prompt += "\nIf latest information is provided, prioritize it."

    return prompt



# ==========================
# 🌐 SEARCH DECISION
def should_use_search(message):
    print("🔥 FUNCTION CALLED:", message)

    if not message:
        return False

    msg = message.lower().strip()

    # ==========================
    # 🔥 REAL-TIME KEYWORDS
    # ==========================
    trigger_words = [
        "today", "live", "latest", "recent",
        "news", "update", "current",
        "score", "match", "ipl",
        "price", "weather", "now",
        "breaking", "happening", "result",
        "who won", "yesterday"
    ]

    for word in trigger_words:
        if word in msg:
            print("✅ TRIGGER WORD:", word)
            return True

    # ==========================
    # ⚡ QUESTION PATTERNS
    # ==========================
    question_patterns = [
        "what is", "who is", "what happened",
        "when is", "who won", "latest"
    ]

    for pattern in question_patterns:
        if pattern in msg:
            print("⚡ QUESTION PATTERN:", pattern)
            return True

    # ==========================
    # ⚡ SHORT QUERY FALLBACK
    # ==========================
    word_count = len(msg.split())

    if word_count <= 3:
        print("⚡ VERY SHORT QUERY → SEARCH")
        return True

    # ==========================
    # ❌ DEFAULT
    # ==========================
    print("❌ NO SEARCH NEEDED")
    return False