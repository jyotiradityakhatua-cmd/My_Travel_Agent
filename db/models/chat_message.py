# from sqlalchemy import Column, String, Text, DateTime
# from sqlalchemy.sql import func
# from app.db.database import Base


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(String, primary_key=True, index=True)
#     chat_id = Column(String, index=True)

#     role = Column(String)  
#     content = Column(Text)

#     created_at = Column(DateTime(timezone=True), server_default=func.now())
# from datetime import datetime
# from app.db.chat_message import ChatMessage

# from sqlalchemy import (
#     Column,
#     Integer,
#     String,
#     Text,
#     DateTime
# )

# from app.db.database import Base


# class ChatMessage(Base):
#     __tablename__ = "chat_messages"  

#     id = Column(
#         Integer,
#         primary_key=True,
#         index=True
#     )

#     chat_id = Column(
#         String,
#         index=True,
#         nullable=False
#     )

#     role = Column(
#         String,
#         nullable=False
#     )  

#     message = Column(
#         Text,
#         nullable=False
#     )

#     created_at = Column(
#         DateTime,
#         default=datetime.utcnow
#     )

from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime,ForeignKey
from app.db.database import Base




# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True)
#     chat_id = Column(String, index=True, nullable=False)
#     role = Column(String, nullable=False)
#     message = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)
    
# PRAGMA table_info(chat_messages);

# class ChatMessage(Base):
#     __tablename__ = "chat_messages"

#     id = Column(Integer, primary_key=True, index=True)
#     chat_id = Column(String, index=True, nullable=False)
#     role = Column(String, nullable=False)
#     message = Column(Text, nullable=False)
#     created_at = Column(DateTime, default=datetime.utcnow)


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    chat_id = Column(
        String,
        ForeignKey("chat_sessions.chat_id"),
        nullable=True
    )

    role = Column(String)

    message = Column(Text)

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )