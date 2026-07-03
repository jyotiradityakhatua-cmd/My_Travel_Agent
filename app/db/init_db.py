# from app.db.database import Base, engine
# from .chat_message import ChatMessage
# from .chat_state import ChatState
from app.db.database import db
import pymongo


def init_db():
    """Create necessary MongoDB indexes for collections used by the app."""
    # Users: ensure unique username and user_id
    db.users.create_index([("user_id", pymongo.ASCENDING)], unique=True)
    db.users.create_index([("username", pymongo.ASCENDING)], unique=True)

    # Chat sessions
    db.chat_sessions.create_index([("chat_id", pymongo.ASCENDING)], unique=True)

    # Chat messages: index by chat_id and created_at for efficient history queries
    db.chat_messages.create_index([("chat_id", pymongo.ASCENDING), ("created_at", pymongo.ASCENDING)])

    return