from apscheduler.schedulers.background import BackgroundScheduler
from app.core.database import SessionLocal
from app.services.chat_history_service import delete_old_chats

def start_cleanup():
    scheduler = BackgroundScheduler()
    scheduler.add_job(run_cleanup, "interval", days=1)
    scheduler.start()

def run_cleanup():
    db = SessionLocal()
    try:
        delete_old_chats(db)
    finally:
        db.close()
