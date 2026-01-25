from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from typing import Optional

from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.groq_service import ask_groq
from app.models.chat import ChatHistory

router = APIRouter()

# -------------------------------------------------
# CHAT ENDPOINT (WORKS WITH OR WITHOUT LOGIN)
# -------------------------------------------------

@router.post("/voice-chat")
async def voice_chat(
    request: Request,
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user),
):
    body = await request.json()
    text = body.get("text", "").strip()

    if not text:
        raise HTTPException(status_code=400, detail="Empty message")

    # Ask Groq
    try:
        response = ask_groq(text)
    except Exception:
        raise HTTPException(status_code=500, detail="AI service error")

    # ✅ Save history ONLY if user is logged in
    if user_id is not None:
        db.add(ChatHistory(
            user_id=user_id,
            message=text,
            response=response,
        ))
        db.commit()

    return {
        "text": response
    }


# -------------------------------------------------
# CHAT HISTORY API (JWT REQUIRED)
# -------------------------------------------------

@router.get("/history")
def get_chat_history(
    db: Session = Depends(get_db),
    user_id: Optional[int] = Depends(get_current_user),
):
    if user_id is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    chats = (
        db.query(ChatHistory)
        .filter(ChatHistory.user_id == user_id)
        .order_by(ChatHistory.created_at.desc())
        .limit(50)
        .all()
    )

    return [
        {
            "id": c.id,
            "message": c.message,
            "response": c.response,
            "created_at": c.created_at,
        }
        for c in chats
    ]
