from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class AutomationTaskBase(BaseModel):
    title: str
    priority: str
    tags: List[str]
    assignee_name: str
    assignee_role: str
    assignee_avatar: str
    reason: str
    border_color: str
    full_width: bool = False
    status: str = "PENDING"

class AutomationTaskCreate(AutomationTaskBase):
    pass

class AutomationTaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    assignee_name: Optional[str] = None
    assignee_role: Optional[str] = None
    assignee_avatar: Optional[str] = None
    reason: Optional[str] = None
    border_color: Optional[str] = None
    full_width: Optional[bool] = None
    status: Optional[str] = None

class AutomationTaskResponse(AutomationTaskBase):
    id: str
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
