from fastapi import Header
from typing import Optional
from app.core.security import decode_token

def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[int]:

    if not authorization:
        return None

    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return None

        payload = decode_token(token)
        return int(payload["sub"])   # ✅ FIX
    except Exception:
        return None
