
from app.db.database import db as mongo_db

def get_db():
    yield mongo_db