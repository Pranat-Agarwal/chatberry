from functools import wraps
from flask import request

from utils.jwt_helper import verify_token, extract_token_from_header
from models.user_model import UserModel


# ==========================
# 🔐 TOKEN REQUIRED (UPDATED)
# ==========================
def token_required(f):
    """
    Supports:
    - Logged-in users (JWT)
    - Guest users (no token)
    """

    @wraps(f)
    def decorated(*args, **kwargs):
        try:
            auth_header = request.headers.get("Authorization")

            token = extract_token_from_header(auth_header)

            # ==========================
            # 👤 GUEST MODE
            # ==========================
            if not token:
                request.user = {"id": None}  # guest
                return f(*args, **kwargs)

            # ==========================
            # 🔍 VERIFY TOKEN
            # ==========================
            result = verify_token(token)

            if not result.get("valid"):
                request.user = {"id": None}  # fallback guest
                return f(*args, **kwargs)

            user_id = result.get("user_id")

            # ==========================
            # 👤 FETCH USER
            # ==========================
            user = UserModel.get_user_by_id(user_id)

            if not user:
                request.user = {"id": None}
                return f(*args, **kwargs)

            # ==========================
            # ✅ AUTHENTICATED USER
            # ==========================
            request.user = {
                "id": str(user["_id"]),
                "email": user.get("email"),
                "name": user.get("name")
            }

            return f(*args, **kwargs)

        except Exception as e:
            print("❌ Auth Middleware Error:", e)

            # fallback to guest
            request.user = {"id": None}
            return f(*args, **kwargs)
        
        finally:
            
            print("\n=== 🔐 AUTH DEBUG START ===")

            auth_header = request.headers.get("Authorization")
            print("AUTH HEADER:", auth_header)

            token = extract_token_from_header(auth_header)
            print("EXTRACTED TOKEN:", token)

            result = verify_token(token) if token else {"valid": False}
            print("VERIFY RESULT:", result)

            if result.get("valid"):
                print("USER_ID FROM TOKEN:", result.get("user_id"))
            else:
                print("❌ INVALID TOKEN")

            print("=== 🔐 AUTH DEBUG END ===\n")

    return decorated