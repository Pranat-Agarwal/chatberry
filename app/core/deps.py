from fastapi import Header
from typing import Optional

def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[int]:
    """
    Returns user_id if JWT is present, else None
    """

    if not authorization:
        return None

    # Example: "Bearer <token>"
    try:
        token = authorization.split(" ")[1]
        # validate token here
        user_id = decode_token(token)
        return user_id
    except Exception:
        return None
