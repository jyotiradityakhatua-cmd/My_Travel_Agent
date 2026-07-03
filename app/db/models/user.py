# from datetime import datetime
# import uuid

# from sqlalchemy import Column, String, DateTime
# from app.db.database import Base


# # class User(Base):
# #     __tablename__ = "users"

# #     user_id = Column(
# #         String,
# #         primary_key=True,
# #         default=lambda: str(uuid.uuid4())
# #     )

# #     username = Column(
# #         String,
# #         unique=True,
# #         nullable=False
# #     )

# #     password = Column(
# #         String,
# #         nullable=False
# #     )

# #     created_at = Column(
# #         DateTime,
# #         default=datetime.utcnow
# #     )

# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(
#         String,
#         primary_key=True,
#         default=lambda: str(uuid.uuid4())
#     )

#     username = Column(String, unique=True)
#     password = Column(String)

import uuid
from datetime import datetime


class User:
    """
    Plain Python stand-in for the old SQLAlchemy User model.
    Maps to/from a doc in the "users" collection, where user_id is
    stored as _id.
    """

    __slots__ = ("user_id", "username", "password", "created_at")

    def __init__(self, user_id=None, username=None, password=None, created_at=None):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.password = password
        self.created_at = created_at or datetime.utcnow()

    @classmethod
    def from_doc(cls, doc: dict) -> "User":
        return cls(
            user_id=doc.get("_id"),
            username=doc.get("username"),
            password=doc.get("password"),
            created_at=doc.get("created_at"),
        )

    def to_doc(self) -> dict:
        return {
            "_id": self.user_id,
            "username": self.username,
            "password": self.password,
            "created_at": self.created_at,
        }