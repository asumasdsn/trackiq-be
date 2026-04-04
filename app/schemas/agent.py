from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AgentCreateRequest(BaseModel):
    name: str = Field(..., description="Unique agent name")
    graph_id: str = Field(..., description="Graph to bind the agent to")
    description: Optional[str] = None
    config: Optional[dict] = Field(default_factory=dict)


class AgentResponse(BaseModel):
    id: str
    name: str
    graph_id: str
    description: Optional[str]
    config: dict
    created_at: datetime

    class Config:
        from_attributes = True
