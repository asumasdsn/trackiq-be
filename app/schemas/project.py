from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ProjectCreate(BaseModel):
    name: str
    lead: str
    progress: Optional[int] = 0
    eta: Optional[str] = None
    status: Optional[str] = "ON TRACK"
    status_color: Optional[str] = None


class ProjectResponse(BaseModel):
    id: str
    name: str
    lead: str
    progress: int
    eta: Optional[str]
    status: str
    status_color: Optional[str]
    automations_count: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
