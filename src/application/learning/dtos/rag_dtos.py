from pydantic import BaseModel
from typing import Optional

class ChatRequest(BaseModel):
    query: str

class ChatResponse(BaseModel):
    response: str
