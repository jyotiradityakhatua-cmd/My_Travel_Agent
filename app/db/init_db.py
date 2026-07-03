# from app.db.database import Base, engine
# from .chat_message import ChatMessage
# from .chat_state import ChatState
from app.db.database import db
import pymongo


def init_db():
    """Create necessary MongoDB indexes for collections used by the app."""
    try:
        # Users: ensure unique username and user_id (sparse allows multiple nulls)
        db.users.create_index([("user_id", pymongo.ASCENDING)], unique=True, sparse=True)
        db.users.create_index([("username", pymongo.ASCENDING)], unique=True, sparse=True)

        # Chat sessions
        db.chat_sessions.create_index([("chat_id", pymongo.ASCENDING)], unique=True, sparse=True)

        # Chat messages: index by chat_id and created_at for efficient history queries
        db.chat_messages.create_index([("chat_id", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)])

    except pymongo.errors.DuplicateKeyError as e:
        # Index may already exist or conflict with existing data; continue startup
        print(f"[INIT_DB] Index creation warning (may already exist): {e}")
    except Exception as e:
        # Log but don't fail startup if index creation fails
        print(f"[INIT_DB] Warning during index creation: {e}")

    return