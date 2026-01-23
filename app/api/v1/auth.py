from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.services.chat_history_service import save_chat

router = APIRouter()

@router.post("/voice-chat")
def voice_chat(
    text: str,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user)
):
    response = f"Echo: {text}"
    save_chat(db, user_id, text, response)
    return {"text": response}
