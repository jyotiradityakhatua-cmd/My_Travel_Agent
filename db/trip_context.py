from sqlalchemy import Column, String, Integer
from app.db.database import Base


class TripContext(Base):
    __tablename__ = "trip_contexts"

    chat_id = Column(String, primary_key=True)

    intent = Column(String, nullable=True)
    source = Column(String, nullable=True)
    destination = Column(String, nullable=True)

    departure_date = Column(String, nullable=True)
    return_date = Column(String, nullable=True)

    days = Column(Integer, nullable=True)