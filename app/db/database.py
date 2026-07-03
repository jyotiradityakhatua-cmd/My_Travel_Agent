
# from sqlalchemy import create_engine
# # from sqlalchemy.ext.declarative import declarative_base
# # from sqlalchemy.orm import sessionmaker
# from sqlalchemy.orm import declarative_base, sessionmaker

# DATABASE_URL = "sqlite:///./travel_agent.db"




# engine = create_engine(
#     DATABASE_URL, connect_args={"check_same_thread": False}  # only for SQLite
# )


# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base = declarative_base()

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker


DATABASE_URL = "sqlite:///./travel_agent.db"


engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    } 
)



SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()




def get_db():
    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# --- MongoDB client (added for migration from SQLite) ----------------------
import os
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME", "travel_agent")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]

# `db` is a pymongo.database.Database instance exported for repositories
# Example usage: from app.db.database import db; db['chat_messages'].insert_one({...})