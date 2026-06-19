# from app.db.database import Base, engine
# from .chat_message import ChatMessage
# from .chat_state import ChatState
import app.db.models


from app.db.database import Base, engine
from .chat_state import ChatState
from app.db.models.user import User
from app.db.models.chat_session import ChatSession
from app.db.models.chat_message import ChatMessage



def init_db():
    Base.metadata.create_all(bind=engine)