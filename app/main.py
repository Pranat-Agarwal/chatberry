from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

# IMPORTANT: import models before create_all
from app.models.user import User
from app.models.chat import ChatHistory

from app.api.v1.voice_chat import router as chat_router
from app.api.v1.auth import router as auth_router
from app.services.cleanup_service import start_cleanup
from app.core.database import Base, engine

app = FastAPI()

# ✅ Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Create DB tables
if engine:
    Base.metadata.create_all(bind=engine)


# Routers
app.include_router(auth_router, prefix="/api/v1/auth")
app.include_router(chat_router, prefix="/api/v1")

@app.on_event("startup")
def startup():
    if engine:
        start_cleanup()


@app.get("/health")
def health():
    return {"status": "ok"}
