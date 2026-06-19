from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    user_id: str
    chat_id: Optional[str] = None
    message: str