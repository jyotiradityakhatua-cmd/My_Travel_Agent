# from fastapi import FastAPI
# from app.api.router import api_router

# app = FastAPI(
# #     title="AI Travel Agent"
# # )

# # app.include_router(api_router)

# from fastapi import FastAPI
# from app.api.router import api_router
# from app.middleware.auth_middleware import AuthMiddleware
# from app.middleware.logging_middleware import LoggingMiddleware
# from app.db.database import Base, engine
# from app.db import models

# app = FastAPI(
#     title="Travel Agent"
#     )

# app.add_middleware(AuthMiddleware)
# app.add_middleware(LoggingMiddleware)

# app.include_router(api_router)



# Base.metadata.create_all(bind=engine)

# from fastapi import FastAPI
from app.api.router import api_router
from app.api.routes.chat import router as chat_router


# from app.db.init_db import init_db

# app = FastAPI()
# init_db()

# app.include_router(api_router)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.router import api_router
from app.db.init_db import init_db
 
init_db()
app = FastAPI()
 
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "null",                      # HTML opened as local file (file://)
        "http://localhost:5173",     # Vite dev server
        "http://localhost:3000",     # React/Next dev server
        "http://localhost:8080",     # Vue dev server
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5500",     # VS Code Live Server
        "http://localhost:5500",
        "http://localhost:11434/api/chat"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
 
app.include_router(api_router)
 