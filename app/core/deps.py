from fastapi import Header, HTTPException
from app.core.security import decode_token

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(401, "Invalid Authorization header")

    token = authorization.split(" ")[1]
    payload = decode_token(token)

    if not payload:
        raise HTTPException(401, "Invalid or expired token")

    return int(payload["sub"])
