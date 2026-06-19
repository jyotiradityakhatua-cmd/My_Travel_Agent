from app.db.trip_context import TripContext




def get_trip_context(db, chat_id):
    return (
        db.query(TripContext)
        .filter(TripContext.chat_id == chat_id)
        .first()
    )


def create_trip_context(db, chat_id):
    context = TripContext(chat_id=chat_id)

    db.add(context)
    db.commit()
    db.refresh(context)

    return context


def save_trip_context(db, context):
    db.add(context)
    db.commit()
    db.refresh(context)

    return context