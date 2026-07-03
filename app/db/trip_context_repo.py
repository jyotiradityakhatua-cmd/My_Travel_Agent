from app.db.database import db as mongo_db
from datetime import datetime



def get_trip_context(db, chat_id):
    return mongo_db.trip_contexts.find_one({"chat_id": chat_id})


def create_trip_context(db, chat_id):
    context = {
        "chat_id": chat_id,
        "created_at": datetime.utcnow(),
        "data": {}
    }
    res = mongo_db.trip_contexts.insert_one(context)
    context["_id"] = res.inserted_id
    return context


def save_trip_context(db, context):
    # Expecting `context` to be a dict containing at least `chat_id`
    mongo_db.trip_contexts.update_one({"chat_id": context.get("chat_id")}, {"$set": context}, upsert=True)
    return mongo_db.trip_contexts.find_one({"chat_id": context.get("chat_id")})