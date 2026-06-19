# from app.db.models.chat_message import ChatMessage


# def save_message(db, chat_id: str, role: str, content: str):
#     msg = ChatMessage(
#         chat_id=chat_id,
#         role=role,
#         content=content
#     )
#     db.add(msg)
#     db.commit()
#     db.refresh(msg)
#     return msg

# def get_chat_history(db, chat_id: str):
#     messages = db.query(ChatMessage)\
#         .filter(ChatMessage.chat_id == chat_id)\
#         .order_by(ChatMessage.id.asc())\
#         .all()

#     return [
#         {"role": m.role, "content": m.content}
#         for m in messages
#     ]

from app.db.models.chat_message import ChatMessage
from sqlalchemy import distinct






def save_message(
    db,
    chat_id,
    role,
    message
):

    print(
        f"SAVING => {chat_id} | {role} | {message[:50]}"
    )

    msg = ChatMessage(
        chat_id=chat_id,
        role=role,
        message=message
    )

    db.add(msg)
    db.commit()
    db.refresh(msg)

    print("MESSAGE SAVED TO DATABASE")

    return msg

def get_chat_history(
    db,
    chat_id
):
    return (
        db.query(ChatMessage)
        .filter(ChatMessage.chat_id == chat_id)
        .order_by(ChatMessage.id.asc())
        .all()
    )






def get_all_chat_ids(db):
    return (
        db.query(ChatMessage.chat_id)
        .distinct()
        .all()
    )