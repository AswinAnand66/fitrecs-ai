from typing import List, Dict, Any
from pydantic import BaseModel

class ChatMessage(BaseModel):
    text: str
    type: str

class ChatRequest(BaseModel):
    message: str
    context: List[Dict[str, Any]] = []

class ChatResponse(BaseModel):
    response: str