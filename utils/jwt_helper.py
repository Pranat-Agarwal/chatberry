import jwt
from datetime import datetime, timedelta
from config.config import Config


# ==========================
# 🔐 GENERATE JWT TOKEN
# ==========================
def generate_token(user_id):
    """
    Create JWT token for user
    """

    try:
        payload = {
            "user_id": user_id,
            "exp": datetime.utcnow() + timedelta(days=7),  # token expiry
            "iat": datetime.utcnow()
        }

        token = jwt.encode(payload, Config.JWT_SECRET, algorithm="HS256")

        # In PyJWT >= 2.0, token is already string
        return token

    except Exception as e:
        print(f"❌ JWT Generate Error: {str(e)}")
        return None


# ==========================
# 🔍 VERIFY JWT TOKEN
# ==========================
def verify_token(token):
    """
    Decode and verify JWT token
    """

    try:
        decoded = jwt.decode(token, Config.JWT_SECRET, algorithms=["HS256"])

        return {
            "valid": True,
            "user_id": decoded.get("user_id")
        }

    except jwt.ExpiredSignatureError:
        return {
            "valid": False,
            "error": "Token expired"
        }

    except jwt.InvalidTokenError:
        return {
            "valid": False,
            "error": "Invalid token"
        }


# ==========================
# 📦 EXTRACT TOKEN FROM HEADER
# ==========================
def extract_token_from_header(auth_header):
    """
    Extract Bearer token from header
    Example:
    Authorization: Bearer <token>
    """

    if not auth_header:
        return None

    try:
        parts = auth_header.split(" ")

        if len(parts) != 2 or parts[0] != "Bearer":
            return None

        return parts[1]

    except Exception:
        return None


# ==========================
# 🧪 OPTIONAL: REFRESH TOKEN
# ==========================
def refresh_token(old_token):
    """
    Generate new token if old one is valid
    """

    result = verify_token(old_token)

    if not result["valid"]:
        return None

    return generate_token(result["user_id"])