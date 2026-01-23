from datetime import datetime, timedelta
from app.models.chat import ChatHistory

def save_chat(db, user_id: int, message: str, response: str):
    db.add(ChatHistory(
        user_id=user_id,
        message=message,
        response=response
    ))
    db.commit()

def delete_old_chats(db):
    cutoff = datetime.utcnow() - timedelta(days=7)
    db.query(ChatHistory).filter(ChatHistory.created_at < cutoff).delete()
    db.commit()
