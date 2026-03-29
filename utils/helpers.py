import uuid
from datetime import datetime
import re


# ==========================
# 🆔 GENERATE UNIQUE ID
# ==========================
def generate_uuid():
    return str(uuid.uuid4())


# ==========================
# ⏰ CURRENT TIMESTAMP
# ==========================
def current_timestamp():
    return datetime.utcnow()


# ==========================
# 🧹 CLEAN TEXT
# ==========================
def clean_text(text):
    if not text:
        return ""

    text = text.strip()
    text = re.sub(r"\s+", " ", text)

    return text


# ==========================
# 🔤 TRUNCATE TEXT
# ==========================
def truncate_text(text, max_length=200):
    if not text:
        return ""

    return text if len(text) <= max_length else text[:max_length] + "..."


# ==========================
# 📁 VALIDATE FILE TYPE
# ==========================
def allowed_file(filename, allowed_extensions):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in allowed_extensions


# ==========================
# 📦 STANDARD API RESPONSE
# ==========================
def success_response(data=None, message="Success"):
    return {
        "success": True,
        "message": message,
        "data": data
    }


def error_response(message="Something went wrong", code=400):
    return {
        "success": False,
        "message": message,
        "code": code
    }


# ==========================
# 🧠 DETECT EMPTY INPUT
# ==========================
def is_empty(value):
    return value is None or value == ""


# ==========================
# 🔍 SAFE GET FROM DICT
# ==========================
def safe_get(data, key, default=None):
    if not isinstance(data, dict):
        return default

    return data.get(key, default)


# ==========================
# 🔡 LOWERCASE SAFE
# ==========================
def safe_lower(text):
    if not isinstance(text, str):
        return ""

    return text.lower()


# ==========================
# 📊 WORD COUNT
# ==========================
def word_count(text):
    if not text:
        return 0

    return len(text.split())


# ==========================
# 🔐 MASK SENSITIVE DATA
# ==========================
def mask_email(email):
    """
    Example:
    pranat@gmail.com → pr****@gmail.com
    """
    if not email or "@" not in email:
        return email

    name, domain = email.split("@")
    masked_name = name[:2] + "*" * (len(name) - 2)

    return f"{masked_name}@{domain}"


# ==========================
# 🧠 FORMAT CHAT TITLE
# ==========================
def generate_chat_title(message):
    """
    Generate short title from first message
    """
    if not message:
        return "New Chat"

    message = clean_text(message)

    return message[:40] + "..." if len(message) > 40 else message


# ==========================
# 🧪 BOOLEAN PARSER
# ==========================
def parse_bool(value):
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        return value.lower() in ["true", "1", "yes"]

    return False