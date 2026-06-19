from sqlalchemy import Column, String, Integer
from app.db.database import Base


class ChatState(Base):
    __tablename__ = "chat_state"

    chat_id        = Column(String, primary_key=True, index=True)
    source         = Column(String, nullable=True)
    destination    = Column(String, nullable=True)
    departure_date = Column(String, nullable=True)
    return_date    = Column(String, nullable=True)
    days           = Column(Integer, nullable=True)


def get_state(db, chat_id: str) -> dict:
    row = db.query(ChatState).filter(ChatState.chat_id == chat_id).first()
    if not row:
        return {"source": None, "destination": None,
                "departure_date": None, "return_date": None, "days": None}
    return {
        "source": row.source, "destination": row.destination,
        "departure_date": row.departure_date, "return_date": row.return_date,
        "days": row.days,
    }


def save_state(db, chat_id: str, data: dict):
    row = db.query(ChatState).filter(ChatState.chat_id == chat_id).first()
    if not row:
        row = ChatState(chat_id=chat_id)
        db.add(row)
    for field in ["source", "destination", "departure_date", "return_date", "days"]:
        val = data.get(field)
        if val not in [None, "", 0]:
            setattr(row, field, val)
    db.commit()
    db.refresh(row)


def clear_state(db, chat_id: str):
    row = db.query(ChatState).filter(ChatState.chat_id == chat_id).first()
    if row:
        row.source = row.destination = row.departure_date = row.return_date = None
        row.days = None
        db.commit()