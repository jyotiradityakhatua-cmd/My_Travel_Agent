# from datetime import datetime
# import uuid

# from sqlalchemy import (
#     Column,
#     String,
#     DateTime,
#     ForeignKey
# )

# from app.db.database import Base


# class ChatSession(Base):
#     __tablename__ = "chat_sessions"

#     chat_id = Column(
#         String,
#         primary_key=True,
#         default=lambda: str(uuid.uuid4())
#     )

#     user_id = Column(
#         String,
#         ForeignKey("users.user_id"),
#         nullable=False
#     )

#     title = Column(String)

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )


import uuid
from datetime import datetime


class ChatSession:
    """
    Plain Python stand-in for the old SQLAlchemy ChatSession model.
    Maps to/from a doc in the "chat_sessions" collection, where chat_id
    is stored as _id. The old ForeignKey("users.user_id") isn't
    enforced by Mongo -- user_id is just stored as a plain field.
    """

    __slots__ = ("chat_id", "user_id", "title", "created_at")

    def __init__(self, chat_id=None, user_id=None, title=None, created_at=None):
        self.chat_id = chat_id or str(uuid.uuid4())
        self.user_id = user_id
        self.title = title
        self.created_at = created_at or datetime.utcnow()

    @classmethod
    def from_doc(cls, doc: dict) -> "ChatSession":
        return cls(
            chat_id=doc.get("_id"),
            user_id=doc.get("user_id"),
            title=doc.get("title"),
            created_at=doc.get("created_at"),
        )

    def to_doc(self) -> dict:
        return {
            "_id": self.chat_id,
            "user_id": self.user_id,
            "title": self.title,
            "created_at": self.created_at,
        }