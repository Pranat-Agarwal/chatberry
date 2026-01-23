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
    response = ask_groq(text)

    # ✅ Save history ONLY if user is logged in
    if user_id:
        chat = ChatHistory(
            user_id=user_id,
            message=text,
            response=response,
        )
        db.add(chat)
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
    user_id: int = Depends(get_current_user),
):
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
