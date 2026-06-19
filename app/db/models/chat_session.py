from datetime import datetime
import uuid

from sqlalchemy import (
    Column,
    String,
    DateTime,
    ForeignKey
)

from app.db.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    chat_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    user_id = Column(
        String,
        ForeignKey("users.user_id"),
        nullable=False
    )

    title = Column(String)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )