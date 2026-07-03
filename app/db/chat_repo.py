# # from app.db.models.chat_message import ChatMessage


# # def save_message(db, chat_id: str, role: str, content: str):
# #     msg = ChatMessage(
# #         chat_id=chat_id,
# #         role=role,
# #         content=content
# #     )
# #     db.add(msg)
# #     db.commit()
# #     db.refresh(msg)
# #     return msg

# # def get_chat_history(db, chat_id: str):
# #     messages = db.query(ChatMessage)\
# #         .filter(ChatMessage.chat_id == chat_id)\
# #         .order_by(ChatMessage.id.asc())\
# #         .all()

# #     return [
# #         {"role": m.role, "content": m.content}
# #         for m in messages
# #     ]

# from app.db.models.chat_message import ChatMessage
# from sqlalchemy import distinct






# def save_message(
#     db,
#     chat_id,
#     role,
#     message
# ):

#     print(
#         f"SAVING => {chat_id} | {role} | {message[:50]}"
#     )

#     msg = ChatMessage(
#         chat_id=chat_id,
#         role=role,
#         message=message
#     )

#     db.add(msg)
#     db.commit()
#     db.refresh(msg)

#     print("MESSAGE SAVED TO DATABASE")

#     return msg

# def get_chat_history(
#     db,
#     chat_id
# ):
#     return (
#         db.query(ChatMessage)
#         .filter(ChatMessage.chat_id == chat_id)
#         .order_by(ChatMessage.id.asc())
#         .all()
#     )






# def get_all_chat_ids(db):
#     return (
#         db.query(ChatMessage.chat_id)
#         .distinct()
#         .all()
#     )




"""
Async database helpers using SQLAlchemy's async session.

Drop-in replacement for the sync chat_repo.py.
The sync versions are kept as _sync_* fallbacks in case any
non-async route still needs them during migration.
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.future import select
from sqlalchemy import distinct
import os
from dotenv import load_dotenv

from app.db.models.chat_message import ChatMessage

load_dotenv()

# SQLite async URL — swap for postgresql+asyncpg://... in production
DATABASE_URL_ASYNC = os.getenv(
    "DATABASE_URL_ASYNC",
    "sqlite+aiosqlite:///./travel_agent.db"
)

async_engine = create_async_engine(
    DATABASE_URL_ASYNC,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL_ASYNC else {},
    echo=False,
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_async_db():
    """FastAPI dependency for async DB sessions."""
    async with AsyncSessionLocal() as session:
        yield session


async def async_save_message(db: AsyncSession, chat_id: str, role: str, message: str):
    print(f"SAVING => {chat_id} | {role} | {message[:50]}")
    msg = ChatMessage(chat_id=chat_id, role=role, message=message)
    db.add(msg)
    await db.commit()
    await db.refresh(msg)
    print("MESSAGE SAVED TO DATABASE")
    return msg


async def async_get_chat_history(db: AsyncSession, chat_id: str):
    result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id.asc())
    )
    return result.scalars().all()


async def async_get_all_chat_ids(db: AsyncSession):
    result = await db.execute(select(distinct(ChatMessage.chat_id)))
    return result.scalars().all()


# ── Sync fallbacks (used by the sync router during migration) ─────────────────

from app.db.models.chat_message import ChatMessage as _ChatMessage


def save_message(db, chat_id: str, role: str, message: str):
    print(f"SAVING => {chat_id} | {role} | {message[:50]}")
    msg = _ChatMessage(chat_id=chat_id, role=role, message=message)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    print("MESSAGE SAVED TO DATABASE")
    return msg


def get_chat_history(db, chat_id: str):
    return (
        db.query(_ChatMessage)
        .filter(_ChatMessage.chat_id == chat_id)
        .order_by(_ChatMessage.id.asc())
        .all()
    )


# --- MongoDB-backed helpers (migration from SQLite) -----------------------
from datetime import datetime
import asyncio
from app.db.database import db as mongo_db


def _mongo_save_message(chat_id: str, role: str, message: str):
    doc = {
        "chat_id": chat_id,
        "role": role,
        "message": message,
        "created_at": datetime.utcnow(),
    }
    res = mongo_db.chat_messages.insert_one(doc)
    doc["_id"] = res.inserted_id
    return doc


def _mongo_get_chat_history(chat_id: str):
    cursor = mongo_db.chat_messages.find({"chat_id": chat_id}).sort("created_at", 1)
    return list(cursor)


async def async_save_message(db, chat_id: str, role: str, message: str):
    """Async wrapper that runs the blocking pymongo call in a thread executor."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _mongo_save_message, chat_id, role, message)


async def async_get_chat_history(db, chat_id: str):
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _mongo_get_chat_history, chat_id)

# Also provide sync mongo helpers for any synchronous codepaths
def save_message_mongo(chat_id: str, role: str, message: str):
    return _mongo_save_message(chat_id, role, message)


def get_chat_history_mongo(chat_id: str):
    return _mongo_get_chat_history(chat_id)
