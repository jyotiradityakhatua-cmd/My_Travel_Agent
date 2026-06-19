
# # import uuid

# # from fastapi import APIRouter

# # from app.schemas.chat_schema import ChatRequest
# # from app.agents.travel_agents import process_chat


# # router = APIRouter()




# # def generate_chat_id():

# #     return str(uuid.uuid4())



# # @router.post("/")
# # async def chat(req: ChatRequest):

# #     chat_id = req.chat_id

# #     if not chat_id:

# #         chat_id = generate_chat_id()



# #     response = await process_chat(
# #         user_id=req.user_id,
# #         chat_id=chat_id,
# #         message=req.message
# #     )



# #     return {
# #         "chat_id": chat_id,
# #         "response": response
# #     }

# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session

# # from app.db.database import get_db
# # from app.agents.travel_agents import process_chat

# # router = APIRouter()


# # @router.post("/chat")
# # async def chat(
# #     message: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
   
# # ):

# #     response = await process_chat(
# #         user_id="demo_user",   
# #         chat_id=chat_id,
# #         message=message
# #     )

# #     return response

# # @router.get("/test")
# # def test(db: Session = Depends(get_db)):

# #     return {
# #         "status": "ok"
# #     }


# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session
# # from pydantic import BaseModel
# # from typing import Optional

# # from app.db.session import get_db
# # from app.agents.travel_agents import process_chat

# # router = APIRouter()




# # class ChatRequest(BaseModel):
# #     message: str
# #     chat_id: Optional[str] = None




# # @router.post("/chat")
# # async def chat(
# # from fastapi import APIRouter
# # from app.memory.chat_store import add, get
# # from app.services.agent import travel_agent

# # router = APIRouter()


# # @router.post("/")
# # def chat(message: str, chat_id: str = "default"):

# #     add(chat_id, "user", message)

# #     response = travel_agent(chat_id, message)

# #     add(chat_id, "assistant", response)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response,
# #         "history": get(chat_id)
# #     }


# # import uuid
# # from fastapi import APIRouter
# # from app.memory.chat_store import add, get
# # from app.services.agent import travel_agent

# # router = APIRouter()


# # @router.post("/")
# # def chat(message: str, chat_id: str | None = None):


# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())

# #     add(chat_id, "user", message)

# #     response = travel_agent(chat_id, message)

# #     add(chat_id, "assistant", response)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response,
# #         "history": get(chat_id)
# #     }



# # from app.memory.chat_store import add, get
# # from app.services.agent import travel_agent





# # @router.post("/")
# # def chat(message: str, chat_id: str | None = None):


# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())


# #     add(chat_id, "user", message)


# #     history = get(chat_id)

# #     response = travel_agent(chat_id, message, history)


# #     add(chat_id, "assistant", response)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response,
# #         "history": get(chat_id)
# #     }
# from uuid import uuid4
# from fastapi import APIRouter
# from fastapi import Depends
# from sqlalchemy.orm import Session
# from app.db.session import get_db
# from app.db.chat_repo import save_message
# from app.memory.chat_store import get as get_memory, add as add_memory
# from app.services.agent import travel_agent
# from app.db.chat_repo import get_chat_history
# from app.db.chat_repo import  get_all_chat_ids
# from app.db.models.chat_session import ChatSession
# from app.db.models.user import User
# from fastapi import HTTPException
# from fastapi.responses import StreamingResponse
# import uuid
# from app.services.llm_service import run_chat_llm
# # @router.post("/")
# # def chat(message: str, chat_id: str | None = None, db: Session = Depends(get_db)):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())


# #     add_memory(chat_id, "user", message)


# #     save_message(db, chat_id, "user", message)

# #     history = get_memory(chat_id)

# #     response = travel_agent(chat_id, message, history)


# #     add_memory(chat_id, "assistant", response)


# #     save_message(db, chat_id, "assistant", response)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response
# #     }

# # @router.post("/")
# # def chat(message: str, chat_id: str | None = None, db: Session = Depends(get_db)):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())

   
# #     save_message(db, chat_id, "user", message)

# #     history = get(chat_id)


# #     response = travel_agent(chat_id, message, history)


# #     save_message(db, chat_id, "assistant", response)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response,
# #         "db":db
# #     }






# # @router.post("/")
# # def chat(
# #     message: str,
# #     chat_id: str,
# #     db: Session = Depends(get_db)
# # ):

# #     response = travel_agent(
# #         chat_id,
# #         message,
# #         db
# #     )

# #     return {
# #         "chat_id": chat_id,
# #         "response": response
# #     }




# router = APIRouter()




# # @router.post("/")
# # def chat(
# #     message: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
# # ):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())

# #     response = travel_agent(chat_id, message, db)

# #     return {
# #         "chat_id": chat_id,
# #         "response": response
# #     }


# # @router.post("/register")
# # def register(
# #     username: str,
# #     password: str,
# #     db: Session = Depends(get_db)
# # ):

# #     existing_user = (
# #         db.query(User)
# #         .filter(User.username == username)
# #         .first()
# #     )

# #     if existing_user:
# #         raise HTTPException(
# #             status_code=400,
# #             detail="Username already exists"
# #         )

# #     user = User(
# #         username=username,
# #         password=password
# #     )

# #     db.add(user)
# #     db.commit()
# #     db.refresh(user)

# #     return {
# #         "user_id": user.user_id,
# #         "username": user.username
# #     }

# # @router.post("/login")
# # def login(
# #     username: str,
# #     password: str,
# #     db: Session = Depends(get_db)
# # ):

# #     user = (
# #         db.query(User)
# #         .filter(User.username == username)
# #         .first()
# #     )

# #     if not user:
# #         raise HTTPException(
# #             status_code=404,
# #             detail="User not found"
# #         )

# #     if user.password != password:
# #         raise HTTPException(
# #             status_code=401,
# #             detail="Invalid password"
# #         )

# #     return {
# #         "user_id": user.user_id,
# #         "username": user.username
# #     }







# # @router.post("/")
# # def chat(
# #     message: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
# # ):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())


# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="user",
# #         message=message
# #     )


# #     response = travel_agent(
# #         chat_id=chat_id,
# #         message=message,
# #         db=db
# #     )


# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="assistant",
# #         message=response
# #     )

# #     return {
# #         "chat_id": chat_id,
# #         "response": response
# #     }


# # from fastapi import APIRouter, Depends
# # from sqlalchemy.orm import Session

# # from app.db.session import get_db
# # from app.db.chat_repo import save_message
# # from app.db.models.chat_session import ChatSession
# # from app.services.agent import travel_agent

# # router = APIRouter()


# # @router.post("/")
# # def chat(
# #     message: str,
# #     user_id: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
# # ):


# #     if not chat_id:
# #         chat_id = str(uuid4())

   
# #     chat_session = (
# #         db.query(ChatSession)
# #         .filter(ChatSession.chat_id == chat_id)
# #         .first()
# #     )

# #     if not chat_session:

# #         chat_session = ChatSession(
# #             chat_id=chat_id,
# #             user_id=user_id,
# #             title=message[:50]
# #         )

# #         db.add(chat_session)
# #         db.commit()


# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="user",
# #         message=message
# # #     )


# # #     response = travel_agent(
# # #         chat_id=chat_id,
# # #         message=message,
# # #         db=db
# # #     )


# # #     save_message(
# # #         db=db,
# # #         chat_id=chat_id,
# # #         role="assistant",
# # #         message=response
# # #     )

# # #     return {
# # #         "user_id": user_id,
# # #         "chat_id": chat_id,
# # #         "response": response
# # #     }



# # # @router.post("/")
# # # def chat(
# # #     message: str,
# # #     user_id: str,
# # #     chat_id: str | None = None,
# # #     db: Session = Depends(get_db)
# # # ):

# # #     if not chat_id:
# # #         chat_id = str(uuid.uuid4())

# # #     chat_session = (
# # #         db.query(ChatSession)
# # #         .filter(ChatSession.chat_id == chat_id)
# # #         .first()
# # #     )

# # #     if not chat_session:
# # #         chat_session = ChatSession(
# # #             chat_id=chat_id,
# # #             user_id=user_id,
# # #             title=message[:50]
# # #         )
# # #         db.add(chat_session)
# # #         db.commit()

# # #     save_message(
# # #         db=db,
# # #         chat_id=chat_id,
# # #         role="user",
# # #         message=message
# # #     )

   
# #     # def stream_response():

# #     #     full_response = ""

# #     #     for chunk in travel_agent_stream(
# #     #         chat_id=chat_id,
# #     #         message=message,
# #     #         db=db
# #     #     ):
# #     #         full_response += chunk
# #     #         yield chunk

# #     #     save_message(
# #     #         db=db,
# #     #         chat_id=chat_id,
# #     #         role="assistant",
# #     #         message=full_response
# #     #     )

# #     # return StreamingResponse(
# #     #     stream_response(),
# #     #     media_type="text/plain"
# #     # )


# # @router.post("/")
# # def chat(
# #     message: str,
# #     user_id: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
# # ):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())

# #     chat_session = (
# #         db.query(ChatSession)
# #         .filter(ChatSession.chat_id == chat_id)
# #         .first()
# #     )

# #     if not chat_session:
# #         chat_session = ChatSession(
# #             chat_id=chat_id,
# #             user_id=user_id,
# #             title=message[:50]
# #         )
# #         db.add(chat_session)
# #         db.commit()

# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="user",
# #         message=message
# #     )


# #     def stream():
# #         full_response = ""

# #         for chunk in travel_agent(chat_id, message, db):
# #             full_response += chunk
# #             yield chunk  
# #         # for chunk in travel_agent(chat_id, message, db):
# #         #      for word in chunk.split(" "):
# #         #          full_response += word + " "
# #         # yield word + " "
  
# #         save_message(
# #             db=db,
# #             chat_id=chat_id,
# #             role="assistant",
# #             message=full_response
# #         )

    
# #         # yield f"\n[CHAT_ID:{chat_id}]"

# #     return StreamingResponse(
# #         stream(),
# #         media_type="text/plain"
# #     )

# # @router.get("/history/{chat_id}")
# # def history(
# #     chat_id: str,
# #     db: Session = Depends(get_db)
# # ):

# #     messages = get_chat_history(
# #         db=db,
# #         chat_id=chat_id
# #     )

# #     return [
# #         {
# #             "id": msg.id,
# #             "role": msg.role,
# #             "message": msg.message,
# #             "created_at": msg.created_at
# #         }
# #         for msg in messages
# #     ]

# # @router.get("/chats")
# # def get_chats(db: Session = Depends(get_db)):

# #     chats = get_all_chat_ids(db)

# #     return [
# #         {
# #             "chat_id": chat[0]
# #         }
# #         for chat in chats
# #     ]


# # @router.get("/users/{user_id}/chats")
# # def get_user_chats(
# #     user_id: str,
# #     db: Session = Depends(get_db)
# # ):

# #     chats = (
# #         db.query(ChatSession)
# #         .filter(ChatSession.user_id == user_id)
# #         .order_by(ChatSession.created_at.desc())
# #         .all()
# #     )

# #     return [
# #         {
# #             "chat_id": chat.chat_id,
# #             "title": chat.title,
# #             "created_at": chat.created_at
# #         }
# #         for chat in chats
# #     ]





# # ── Auth ──────────────────────────────────────────────────────────────────────

# @router.post("/register")
# def register(username: str, password: str, db: Session = Depends(get_db)):
#     if db.query(User).filter(User.username == username).first():
#         raise HTTPException(status_code=400, detail="Username already exists")
#     user = User(username=username, password=password)
#     db.add(user)
#     db.commit()
#     db.refresh(user)
#     return {"user_id": user.user_id, "username": user.username}


# @router.post("/login")
# def login(username: str, password: str, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.username == username).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")
#     if user.password != password:
#         raise HTTPException(status_code=401, detail="Invalid password")
#     return {"user_id": user.user_id, "username": user.username}


# # ── Chat ──────────────────────────────────────────────────────────────────────

# @router.post("/")
# def chat(
#     message: str,
#     user_id: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db),
# ):
#     is_new = not chat_id
#     if is_new:
#         chat_id = str(uuid.uuid4())

#     # Create session row if needed
#     if not db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first():
#         db.add(ChatSession(
#             chat_id=chat_id,
#             user_id=user_id,
#             title=message[:50]
#         ))
#         db.commit()

#     # Persist user message before streaming
#     save_message(db=db, chat_id=chat_id, role="user", message=message)

#     def stream():
#         full = ""
#         for chunk in travel_agent(chat_id, message, db):
#             full += chunk
#             yield chunk
#         # Persist assistant reply
#         save_message(db=db, chat_id=chat_id, role="assistant", message=full)
#         # Send chat_id so frontend knows which session this is
#         yield f"\n\n<!--CHAT_ID:{chat_id}-->"

#     return StreamingResponse(stream(), media_type="text/plain")


# # ── History & user chats ──────────────────────────────────────────────────────

# @router.get("/history/{chat_id}")
# def history(chat_id: str, db: Session = Depends(get_db)):
#     msgs = get_chat_history(db=db, chat_id=chat_id)
#     return [
#         {"id": m.id, "role": m.role, "message": m.message, "created_at": m.created_at}
#         for m in msgs
#     ]


# @router.get("/users/{user_id}/chats")
# def get_user_chats(user_id: str, db: Session = Depends(get_db)):
#     chats = (
#         db.query(ChatSession)
#         .filter(ChatSession.user_id == user_id)
#         .order_by(ChatSession.created_at.desc())
#         .all()
#     )
#     return [
#         {"chat_id": c.chat_id, "title": c.title, "created_at": c.created_at}
#         for c in chats
#     ]


# @router.post("/chat")
# def chat_endpoint(payload: dict):
#     ctx = payload["ctx"]
#     user_query = payload["message"]

#     reply = run_chat_llm(ctx, user_query)

#     return {"response": reply}

    

    # import uuid

# from fastapi import APIRouter

# from app.schemas.chat_schema import ChatRequest
# from app.agents.travel_agents import process_chat


# router = APIRouter()




# def generate_chat_id():

#     return str(uuid.uuid4())



# @router.post("/")
# async def chat(req: ChatRequest):

#     chat_id = req.chat_id

#     if not chat_id:

#         chat_id = generate_chat_id()



#     response = await process_chat(
#         user_id=req.user_id,
#         chat_id=chat_id,
#         message=req.message
#     )



#     return {
#         "chat_id": chat_id,
#         "response": response
#     }

# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.db.database import get_db
# from app.agents.travel_agents import process_chat

# router = APIRouter()


# @router.post("/chat")
# async def chat(
#     message: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db)
   
# ):

#     response = await process_chat(
#         user_id="demo_user",   
#         chat_id=chat_id,
#         message=message
#     )

#     return response

# @router.get("/test")
# def test(db: Session = Depends(get_db)):

#     return {
#         "status": "ok"
#     }


# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from pydantic import BaseModel
# from typing import Optional

# from app.db.session import get_db
# from app.agents.travel_agents import process_chat

# router = APIRouter()




# class ChatRequest(BaseModel):
#     message: str
#     chat_id: Optional[str] = None




# @router.post("/chat")
# async def chat(
# from fastapi import APIRouter
# from app.memory.chat_store import add, get
# from app.services.agent import travel_agent

# router = APIRouter()


# @router.post("/")
# def chat(message: str, chat_id: str = "default"):

#     add(chat_id, "user", message)

#     response = travel_agent(chat_id, message)

#     add(chat_id, "assistant", response)

#     return {
#         "chat_id": chat_id,
#         "response": response,
#         "history": get(chat_id)
#     }


# import uuid
# from fastapi import APIRouter
# from app.memory.chat_store import add, get
# from app.services.agent import travel_agent

# router = APIRouter()


# @router.post("/")
# def chat(message: str, chat_id: str | None = None):


#     if not chat_id:
#         chat_id = str(uuid.uuid4())

#     add(chat_id, "user", message)

#     response = travel_agent(chat_id, message)

#     add(chat_id, "assistant", response)

#     return {
#         "chat_id": chat_id,
#         "response": response,
#         "history": get(chat_id)
#     }



# from app.memory.chat_store import add, get
# from app.services.agent import travel_agent





# @router.post("/")
# def chat(message: str, chat_id: str | None = None):


#     if not chat_id:
#         chat_id = str(uuid.uuid4())


#     add(chat_id, "user", message)


#     history = get(chat_id)

#     response = travel_agent(chat_id, message, history)


#     add(chat_id, "assistant", response)

#     return {
#         "chat_id": chat_id,
#         "response": response,
#         "history": get(chat_id)
#     }
from uuid import uuid4
from fastapi import APIRouter
from fastapi import Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.chat_repo import save_message
from app.memory.chat_store import get as get_memory, add as add_memory
from app.services.agent import travel_agent
from app.db.chat_repo import get_chat_history
from app.db.chat_repo import  get_all_chat_ids
from app.db.models.chat_session import ChatSession
from app.db.models.user import User
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import uuid
from app.services.llm_service import run_chat_llm
from dotenv import load_dotenv
# ── New imports for Google Maps / hotel & place lookup (SearchAPI.io) ────────
import os
import requests
from typing import Optional
from fastapi import Query
# @router.post("/")
# def chat(message: str, chat_id: str | None = None, db: Session = Depends(get_db)):

#     if not chat_id:
#         chat_id = str(uuid.uuid4())


#     add_memory(chat_id, "user", message)


#     save_message(db, chat_id, "user", message)

#     history = get_memory(chat_id)

#     response = travel_agent(chat_id, message, history)


#     add_memory(chat_id, "assistant", response)


#     save_message(db, chat_id, "assistant", response)

#     return {
#         "chat_id": chat_id,
#         "response": response
#     }

# @router.post("/")
# def chat(message: str, chat_id: str | None = None, db: Session = Depends(get_db)):

#     if not chat_id:
#         chat_id = str(uuid.uuid4())

   
#     save_message(db, chat_id, "user", message)

#     history = get(chat_id)


#     response = travel_agent(chat_id, message, history)


#     save_message(db, chat_id, "assistant", response)

#     return {
#         "chat_id": chat_id,
#         "response": response,
#         "db":db
#     }






# @router.post("/")
# def chat(
#     message: str,
#     chat_id: str,
#     db: Session = Depends(get_db)
# ):

#     response = travel_agent(
#         chat_id,
#         message,
#         db
#     )

#     return {
#         "chat_id": chat_id,
#         "response": response
#     }




router = APIRouter()
load_dotenv()


# @router.post("/")
# def chat(
#     message: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db)
# ):

#     if not chat_id:
#         chat_id = str(uuid.uuid4())

#     response = travel_agent(chat_id, message, db)

#     return {
#         "chat_id": chat_id,
#         "response": response
#     }


# @router.post("/register")
# def register(
#     username: str,
#     password: str,
#     db: Session = Depends(get_db)
# ):

#     existing_user = (
#         db.query(User)
#         .filter(User.username == username)
#         .first()
#     )

#     if existing_user:
#         raise HTTPException(
#             status_code=400,
#             detail="Username already exists"
#         )

#     user = User(
#         username=username,
#         password=password
#     )

#     db.add(user)
#     db.commit()
#     db.refresh(user)

#     return {
#         "user_id": user.user_id,
#         "username": user.username
#     }

# @router.post("/login")
# def login(
#     username: str,
#     password: str,
#     db: Session = Depends(get_db)
# ):

#     user = (
#         db.query(User)
#         .filter(User.username == username)
#         .first()
#     )

#     if not user:
#         raise HTTPException(
#             status_code=404,
#             detail="User not found"
#         )

#     if user.password != password:
#         raise HTTPException(
#             status_code=401,
#             detail="Invalid password"
#         )

#     return {
#         "user_id": user.user_id,
#         "username": user.username
#     }







# @router.post("/")
# def chat(
#     message: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db)
# ):

#     if not chat_id:
#         chat_id = str(uuid.uuid4())


#     save_message(
#         db=db,
#         chat_id=chat_id,
#         role="user",
#         message=message
#     )


#     response = travel_agent(
#         chat_id=chat_id,
#         message=message,
#         db=db
#     )


#     save_message(
#         db=db,
#         chat_id=chat_id,
#         role="assistant",
#         message=response
#     )

#     return {
#         "chat_id": chat_id,
#         "response": response
#     }


# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.db.session import get_db
# from app.db.chat_repo import save_message
# from app.db.models.chat_session import ChatSession
# from app.services.agent import travel_agent

# router = APIRouter()


# @router.post("/")
# def chat(
#     message: str,
#     user_id: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db)
# ):


#     if not chat_id:
#         chat_id = str(uuid4())

   
#     chat_session = (
#         db.query(ChatSession)
#         .filter(ChatSession.chat_id == chat_id)
#         .first()
#     )

#     if not chat_session:

#         chat_session = ChatSession(
#             chat_id=chat_id,
#             user_id=user_id,
#             title=message[:50]
#         )

#         db.add(chat_session)
#         db.commit()


#     save_message(
#         db=db,
#         chat_id=chat_id,
#         role="user",
#         message=message
# #     )


# #     response = travel_agent(
# #         chat_id=chat_id,
# #         message=message,
# #         db=db
# #     )


# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="assistant",
# #         message=response
# #     )

# #     return {
# #         "user_id": user_id,
# #         "chat_id": chat_id,
# #         "response": response
# #     }



# # @router.post("/")
# # def chat(
# #     message: str,
# #     user_id: str,
# #     chat_id: str | None = None,
# #     db: Session = Depends(get_db)
# # ):

# #     if not chat_id:
# #         chat_id = str(uuid.uuid4())

# #     chat_session = (
# #         db.query(ChatSession)
# #         .filter(ChatSession.chat_id == chat_id)
# #         .first()
# #     )

# #     if not chat_session:
# #         chat_session = ChatSession(
# #             chat_id=chat_id,
# #             user_id=user_id,
# #             title=message[:50]
# #         )
# #         db.add(chat_session)
# #         db.commit()

# #     save_message(
# #         db=db,
# #         chat_id=chat_id,
# #         role="user",
# #         message=message
# #     )

   
#     # def stream_response():

#     #     full_response = ""

#     #     for chunk in travel_agent_stream(
#     #         chat_id=chat_id,
#     #         message=message,
#     #         db=db
#     #     ):
#     #         full_response += chunk
#     #         yield chunk

#     #     save_message(
#     #         db=db,
#     #         chat_id=chat_id,
#     #         role="assistant",
#     #         message=full_response
#     #     )

#     # return StreamingResponse(
#     #     stream_response(),
#     #     media_type="text/plain"
#     # )


# @router.post("/")
# def chat(
#     message: str,
#     user_id: str,
#     chat_id: str | None = None,
#     db: Session = Depends(get_db)
# ):

#     if not chat_id:
#         chat_id = str(uuid.uuid4())

#     chat_session = (
#         db.query(ChatSession)
#         .filter(ChatSession.chat_id == chat_id)
#         .first()
#     )

#     if not chat_session:
#         chat_session = ChatSession(
#             chat_id=chat_id,
#             user_id=user_id,
#             title=message[:50]
#         )
#         db.add(chat_session)
#         db.commit()

#     save_message(
#         db=db,
#         chat_id=chat_id,
#         role="user",
#         message=message
#     )


#     def stream():
#         full_response = ""

#         for chunk in travel_agent(chat_id, message, db):
#             full_response += chunk
#             yield chunk  
#         # for chunk in travel_agent(chat_id, message, db):
#         #      for word in chunk.split(" "):
#         #          full_response += word + " "
#         # yield word + " "
  
#         save_message(
#             db=db,
#             chat_id=chat_id,
#             role="assistant",
#             message=full_response
#         )

    
#         # yield f"\n[CHAT_ID:{chat_id}]"

#     return StreamingResponse(
#         stream(),
#         media_type="text/plain"
#     )

# @router.get("/history/{chat_id}")
# def history(
#     chat_id: str,
#     db: Session = Depends(get_db)
# ):

#     messages = get_chat_history(
#         db=db,
#         chat_id=chat_id
#     )

#     return [
#         {
#             "id": msg.id,
#             "role": msg.role,
#             "message": msg.message,
#             "created_at": msg.created_at
#         }
#         for msg in messages
#     ]

# @router.get("/chats")
# def get_chats(db: Session = Depends(get_db)):

#     chats = get_all_chat_ids(db)

#     return [
#         {
#             "chat_id": chat[0]
#         }
#         for chat in chats
#     ]


# @router.get("/users/{user_id}/chats")
# def get_user_chats(
#     user_id: str,
#     db: Session = Depends(get_db)
# ):

#     chats = (
#         db.query(ChatSession)
#         .filter(ChatSession.user_id == user_id)
#         .order_by(ChatSession.created_at.desc())
#         .all()
#     )

#     return [
#         {
#             "chat_id": chat.chat_id,
#             "title": chat.title,
#             "created_at": chat.created_at
#         }
#         for chat in chats
#     ]





# ── Auth ──────────────────────────────────────────────────────────────────────

@router.post("/register")
def register(username: str, password: str, db: Session = Depends(get_db)):
    if db.query(User).filter(User.username == username).first():
        raise HTTPException(status_code=400, detail="Username already exists")
    user = User(username=username, password=password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return {"user_id": user.user_id, "username": user.username}


@router.post("/login")
def login(username: str, password: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.password != password:
        raise HTTPException(status_code=401, detail="Invalid password")
    return {"user_id": user.user_id, "username": user.username}


# ── Chat ──────────────────────────────────────────────────────────────────────

@router.post("/")
def chat(
    message: str,
    user_id: str,
    chat_id: str | None = None,
    db: Session = Depends(get_db),
):
    is_new = not chat_id
    if is_new:
        chat_id = str(uuid.uuid4())

    # Create session row if needed
    if not db.query(ChatSession).filter(ChatSession.chat_id == chat_id).first():
        db.add(ChatSession(
            chat_id=chat_id,
            user_id=user_id,
            title=message[:50]
        ))
        db.commit()

    # Persist user message before streaming
    save_message(db=db, chat_id=chat_id, role="user", message=message)

    def stream():
        full = ""
        for chunk in travel_agent(chat_id, message, db):
            full += chunk
            yield chunk
        # Persist assistant reply
        save_message(db=db, chat_id=chat_id, role="assistant", message=full)
        # Send chat_id so frontend knows which session this is
        yield f"\n\n<!--CHAT_ID:{chat_id}-->"

    return StreamingResponse(stream(), media_type="text/plain")


# ── History & user chats ──────────────────────────────────────────────────────

@router.get("/history/{chat_id}")
def history(chat_id: str, db: Session = Depends(get_db)):
    msgs = get_chat_history(db=db, chat_id=chat_id)
    return [
        {"id": m.id, "role": m.role, "message": m.message, "created_at": m.created_at}
        for m in msgs
    ]


@router.get("/users/{user_id}/chats")
def get_user_chats(user_id: str, db: Session = Depends(get_db)):
    chats = (
        db.query(ChatSession)
        .filter(ChatSession.user_id == user_id)
        .order_by(ChatSession.created_at.desc())
        .all()
    )
    return [
        {"chat_id": c.chat_id, "title": c.title, "created_at": c.created_at}
        for c in chats
    ]


@router.post("/chat")
def chat_endpoint(payload: dict):
    ctx = payload["ctx"]
    user_query = payload["message"]

    reply = run_chat_llm(ctx, user_query)

    return {"response": reply}


# ── Places / Hotels (Google Maps via SearchAPI.io) ───────────────────────────
# New feature: lets the frontend map panel look up real coordinates for hotels
# and itinerary places without doing client-side geocoding. The SearchAPI key
# stays server-side as an env var — never put it in frontend code.
#
# Setup:
#   1. pip install requests
#   2. export SEARCHAPI_KEY="your_searchapi_io_key"
#
# Frontend calls:
#   GET /places/batch?queries=Casa Frei Goa,Fort Aguada Goa
#   GET /places/search?q=Casa Frei Goa

SEARCHAPI_KEY = os.environ.get("SERP_API_KEY")
SEARCHAPI_URL = "https://www.searchapi.io/api/v1/search"


@router.get("/places/search")
def search_places(
    q: str = Query(..., description="Search term, e.g. 'Casa Frei Goa' or 'Hotels'"),
    lat: Optional[float] = Query(None, description="Latitude to bias results"),
    lng: Optional[float] = Query(None, description="Longitude to bias results"),
    zoom: int = Query(13, description="Google Maps zoom level for the ll param"),
):
    """
    Looks up a place/hotel by name (optionally biased to a lat/lng) and returns
    a small, clean payload with coordinates the frontend can plot directly.
    """
    if not SEARCHAPI_KEY:
        raise HTTPException(
            status_code=500,
            detail="SEARCHAPI_KEY environment variable is not set on the server.",
        )

    params = {
        "engine": "google_maps",
        "q": q,
        "api_key": SEARCHAPI_KEY,
    }
    if lat is not None and lng is not None:
        params["ll"] = f"@{lat},{lng},{zoom}z"

    try:
        resp = requests.get(SEARCHAPI_URL, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=f"SearchAPI request failed: {e}")

    data = resp.json()
    local_results = data.get("local_results", [])

    places = []
    for r in local_results:
        coords = r.get("gps_coordinates")
        if not coords:
            continue
        places.append({
            "name": r.get("title"),
            "address": r.get("address"),
            "lat": coords.get("latitude"),
            "lng": coords.get("longitude"),
            "rating": r.get("rating"),
            "reviews": r.get("reviews"),
            "price": r.get("price"),
            "type": r.get("type"),
            "thumbnail": r.get("thumbnail"),
            "place_id": r.get("place_id"),
        })

    return {"query": q, "places": places}


@router.get("/places/batch")
def search_places_batch(
    queries: str = Query(..., description="Comma-separated list of search terms"),
    lat: Optional[float] = Query(None),
    lng: Optional[float] = Query(None),
):
    """
    Pass several names at once (e.g. every hotel/place extracted from one
    itinerary response) and get back one combined list. Calls SearchAPI once
    per query under the hood — keep batches small (under ~15) to control cost.
    """
    terms = [t.strip() for t in queries.split(",") if t.strip()]
    all_places = []
    for term in terms[:15]:
        result = search_places(q=term, lat=lat, lng=lng)
        if result["places"]:
            all_places.append(result["places"][0])  # take the best match only
    return {"places": all_places}