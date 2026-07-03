from datetime import datetime, timezone


def save_message(
    db,
    chat_id,
    role,
    message
):

    print(
        f"SAVING => {chat_id} | {role} | {message[:50]}"
    )

    doc = {
        "chat_id": chat_id,
        "role": role,
        "message": message,
        "created_at": datetime.now(timezone.utc),
    }

    result = db["chat_messages"].insert_one(doc)
    doc["_id"] = result.inserted_id

    print("MESSAGE SAVED TO DATABASE")

    return doc


def get_chat_history(
    db,
    chat_id
):
    cursor = (
        db["chat_messages"]
        .find({"chat_id": chat_id})
        .sort("created_at", 1)
    )
    return list(cursor)


def get_all_chat_ids(db):
    return db["chat_messages"].distinct("chat_id")