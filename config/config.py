import os
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()


class Config:
    # ==========================
    # 🔐 SECURITY
    # ==========================
    SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
    JWT_SECRET = os.getenv("JWT_SECRET", "jwtsecretkey")

    # ==========================
    # 🗄️ DATABASE
    # ==========================
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    DB_NAME = os.getenv("DB_NAME", "ai_chatbot")

    # ==========================
    # 🤖 AI CONFIG (GROQ)
    # ==========================
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama3-70b-8192")

    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

    GOOGLE_CLIENT_ID=os.getenv("950880637924-2pgj63ev1hgb635s1imnjjvon9tto8n0.apps.googleusercontent.com")

    # ==========================
    # 📁 FILE UPLOAD
    # ==========================
    UPLOAD_FOLDER = os.getenv("UPLOAD_FOLDER", "uploads")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    ALLOWED_EXTENSIONS = {"txt", "png", "jpg", "jpeg"}

    # ==========================
    # 🔊 TEXT TO SPEECH
    # ==========================
    TTS_ENGINE = os.getenv("TTS_ENGINE", "gtts")  # or 'pyttsx3'

    # ==========================
    # 🌍 SERVER
    # ==========================
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 5000))
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # ==========================
    # 🧠 CONTEXT ENGINE SETTINGS
    # ==========================
    MAX_HISTORY_MESSAGES = 20  # limit chat history for performance
    DEFAULT_QUERY_TYPE = "line"  # word / line / paragraph

    # ==========================
    # ⚡ PERFORMANCE
    # ==========================
    REQUEST_TIMEOUT = 30  # seconds


# ==========================
# ✅ HELPER FUNCTIONS
# ==========================

def validate_config():
    """
    Ensure required environment variables are set
    """
    required_keys = [
        "GROQ_API_KEY",
        "TAVILY_API_KEY",
        "MONGO_URI",
        "JWT_SECRET"
    ]

    missing = [key for key in required_keys if not os.getenv(key)]

    if missing:
        raise Exception(f"❌ Missing environment variables: {', '.join(missing)}")

    print("✅ Configuration validated successfully")