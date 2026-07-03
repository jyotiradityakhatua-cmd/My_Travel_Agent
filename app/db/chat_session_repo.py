from app.db.models.chat_session import ChatSession


def get_session(db, chat_id):
    doc = db["chat_sessions"].find_one({"_id": chat_id})
    if not doc:
        return None
    return ChatSession.from_doc(doc)


def create_session(db, chat_id, user_id, title):
    session = ChatSession(chat_id=chat_id, user_id=user_id, title=title)
    db["chat_sessions"].insert_one(session.to_doc())
    return session


def get_sessions_by_user(db, user_id):
    cursor = (
        db["chat_sessions"]
        .find({"user_id": user_id})
        .sort("created_at", -1)
    )
    return [ChatSession.from_doc(doc) for doc in cursor]