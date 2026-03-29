import os
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from flask import current_app, g

# Global client (singleton)
client = None


def get_db():
    """
    Get database instance (per request safe)
    """
    if "db" not in g:
        mongo_uri = current_app.config.get("MONGO_URI")
        db_name = current_app.config.get("DB_NAME")

        g.client = MongoClient(mongo_uri)
        g.db = g.client[db_name]

    return g.db


def close_db(e=None):
    """
    Close DB connection after request
    """
    client = g.pop("client", None)

    if client is not None:
        client.close()


def init_db(app):
    """
    Initialize MongoDB with Flask app
    """
    try:
        print("MONGO_URI:", app.config.get("MONGO_URI"))
        mongo_uri = app.config.get("MONGO_URI")
        db_name = app.config.get("DB_NAME")

        global client
        client = MongoClient(mongo_uri)

        # Test connection
        client.admin.command("ping")

        print("✅ MongoDB connected successfully")

        # Store DB in app config
        app.config["DB"] = client[db_name]

        # Register teardown
        app.teardown_appcontext(close_db)

    except ConnectionFailure as e:
        print("❌ MongoDB connection failed:", str(e))
        raise e


# ==========================
# 📦 COLLECTION HELPERS
# ==========================

def get_users_collection():
    db = current_app.config["DB"]
    return db["users"]


def get_chats_collection():
    db = current_app.config["DB"]
    return db["chats"]


def get_profile_collection():
    db = current_app.config["DB"]
    return db["profile"]


# ==========================
# ⚡ INDEX SETUP (IMPORTANT)
# ==========================

def create_indexes():
    """
    Create indexes for performance (call once)
    """
    db = client[os.getenv("DB_NAME")]

    # Users: unique email
    db["users"].create_index("email", unique=True)

    # Chats: faster lookup
    db["chats"].create_index("user_id")
    db["chats"].create_index("session_id")

    # Profile: one per user
    db["profile"].create_index("user_id", unique=True)

    print("✅ Indexes created successfully")