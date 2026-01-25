from fastapi import Header
from typing import Optional

from app.core.security import decode_token


def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[int]:
    """
    Returns user_id if JWT is valid, else None
    """

    if not authorization:
        return None

    # Expected format: "Bearer <token>"
    try:
        scheme, token = authorization.split(" ")
        if scheme.lower() != "bearer":
            return None

        payload = decode_token(token)
        if not payload:
            return None

        return int(payload.get("sub"))

    except Exception:
        return None
