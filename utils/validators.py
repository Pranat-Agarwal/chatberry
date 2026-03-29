import re
# ==========================
# 🧠 TEXT INPUT VALIDATION
# ==========================
def validate_text_input(text: str, min_len=1, max_len=5000) -> bool:
    """
    Validate general text input
    """

    if not text:
        return False

    text = text.strip()

    if len(text) < min_len or len(text) > max_len:
        return False

    return True


# ==========================
# 📁 FILE VALIDATION
# ==========================
def validate_file(filename: str, allowed_extensions: set) -> bool:
    """
    Validate uploaded file type
    """

    if not filename or "." not in filename:
        return False

    ext = filename.rsplit(".", 1)[1].lower()

    return ext in allowed_extensions


# ==========================
# 🆔 SESSION ID VALIDATION
# ==========================
def validate_session_id(session_id: str) -> bool:
    """
    Validate session ID (UUID format)
    """

    if not session_id:
        return False

    pattern = r"^[a-f0-9\-]{36}$"
    return re.match(pattern, session_id) is not None


# ==========================
# 🔢 GENERIC LENGTH CHECK
# ==========================
def validate_length(value: str, min_len=1, max_len=255) -> bool:
    if not value:
        return False

    return min_len <= len(value) <= max_len


# ==========================
# 🧠 KEY-VALUE VALIDATION (MEMORY)
# ==========================
def validate_key_value(key, value):
    """
    Validate memory key-value pair
    """

    if not key or not isinstance(key, str):
        return False

    if len(key) > 100:
        return False

    if value is None:
        return False

    return True


# ==========================
# 🚫 SANITIZE INPUT
# ==========================
def sanitize_input(text: str) -> str:
    """
    Remove potentially harmful characters
    """

    if not text:
        return ""

    # Remove script tags (basic protection)
    text = re.sub(r"<.*?>", "", text)

    # Remove excessive whitespace
    text = re.sub(r"\s+", " ", text)

    return text.strip()