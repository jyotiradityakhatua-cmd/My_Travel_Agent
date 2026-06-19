
from pydantic import BaseModel
from typing import Any, Optional




class APIResponse(BaseModel):
    success: bool = True
    message: str
    data: Optional[Any] = None




class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    error_code: Optional[str] = None



class ChatResponse(BaseModel):
    chat_id: str
    message: str
    itinerary: Optional[str] = None
    memory_used: Optional[list] = None

