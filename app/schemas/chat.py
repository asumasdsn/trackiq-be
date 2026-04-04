from pydantic import BaseModel, Field
from typing import Optional, List


class Message(BaseModel):
    role: str = Field(..., description="'human', 'ai', or 'system'")
    content: str


class ChatRequest(BaseModel):
    thread_id: Optional[str] = None
    agent_id: Optional[str] = None
    message: str
    history: Optional[List[Message]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    thread_id: str
    reply: str
    usage: Optional[dict] = None
