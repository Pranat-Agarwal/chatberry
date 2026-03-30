import os
from flask import Flask, render_template
from dotenv import load_dotenv

# ==========================
# 🔑 LOAD ENV VARIABLES
# ==========================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

# Debug (optional)
print("ENV MONGO_URI:", os.getenv("MONGO_URI"))

# ==========================
# 🔗 IMPORT BLUEPRINTS
# ==========================
from routes.auth_routes import auth_bp
from routes.chat_routes import chat_bp
from routes.user_routes import user_bp
from routes.file_routes import file_bp
from routes.speech_routes import speech_bp

# ==========================
# 🗄️ DATABASE
# ==========================
from config.database import init_db


def chatberry():
    app = Flask(__name__)

    # ==========================
    # 🔐 CONFIG
    # ==========================
    app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey")

    app.config["UPLOAD_FOLDER"] = "uploads"
    app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB

    # Mongo Config
    app.config["MONGO_URI"] = os.getenv("MONGO_URI")
    app.config["DB_NAME"] = os.getenv("DB_NAME")

    # Google Config
    app.config["GOOGLE_CLIENT_ID"] = os.getenv("GOOGLE_CLIENT_ID")

    # ==========================
    # 🧪 DEBUG CHECKS
    # ==========================
    if not app.config["MONGO_URI"]:
        print("❌ MONGO_URI missing in .env")

    if not app.config["GOOGLE_CLIENT_ID"]:
        print("⚠️ GOOGLE_CLIENT_ID missing (Google login won't work)")

    print("✅ Config Loaded")

    # ==========================
    # 🗄️ INIT DATABASE
    # ==========================
    init_db(app)

    # ==========================
    # 🔗 REGISTER ROUTES
    # ==========================
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(chat_bp, url_prefix="/chat")
    app.register_blueprint(user_bp, url_prefix="/user")
    app.register_blueprint(file_bp, url_prefix="/file")
    app.register_blueprint(speech_bp, url_prefix="/speech")

    # ==========================
    # 🌐 FRONTEND ROUTES
    # ==========================

    @app.route("/")
    def chat_ui():
        return render_template("dashboard/chat.html")

    # ==========================
    # 🧪 HEALTH CHECK
    # ==========================
    @app.route("/health")
    def health():
        return {
            "status": "ok",
            "message": "Server running 🚀"
        }

    return app


# ==========================
# ▶️ RUN SERVER
# ==========================
if __name__ == "__main__":
    app = chatberry()

    port = int(os.getenv("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=True
    )