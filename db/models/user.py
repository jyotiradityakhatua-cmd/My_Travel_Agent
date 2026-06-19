from datetime import datetime
import uuid

from sqlalchemy import Column, String, DateTime
from app.db.database import Base


# class User(Base):
#     __tablename__ = "users"

#     user_id = Column(
#         String,
#         primary_key=True,
#         default=lambda: str(uuid.uuid4())
#     )

#     username = Column(
#         String,
#         unique=True,
#         nullable=False
#     )

#     password = Column(
#         String,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

class User(Base):
    __tablename__ = "users"

    user_id = Column(
        String,
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )

    username = Column(String, unique=True)
    password = Column(String)