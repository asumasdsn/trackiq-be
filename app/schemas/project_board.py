from pydantic import BaseModel
from typing import List, Optional, Any, Dict
from datetime import datetime

class TaskCommentBase(BaseModel):
    content: str
    author_name: str
    author_avatar: str

class TaskCommentResponse(TaskCommentBase):
    id: str
    task_id: str
    created_at: datetime
    class Config:
        from_attributes = True

class BoardTaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    assignee_name: Optional[str] = None
    assignee_avatar: Optional[str] = None
    reporter_name: Optional[str] = None
    reporter_avatar: Optional[str] = None
    priority: str = "Medium"
    identifier: str
    labels: List[str] = []
    due_date: Optional[datetime] = None
    github_data: Optional[Dict[str, Any]] = {}

class BoardTaskCreate(BoardTaskBase):
    column_id: str
    epic_id: Optional[str] = None

class BoardTaskResponse(BoardTaskBase):
    id: str
    column_id: str
    epic_id: Optional[str] = None
    created_at: datetime
    comments: List[TaskCommentResponse] = []
    class Config:
        from_attributes = True

class BoardEpicBase(BaseModel):
    name: str
    color: str = "bg-slate-100"

class BoardEpicResponse(BoardEpicBase):
    id: str
    board_id: str
    class Config:
        from_attributes = True

class BoardColumnBase(BaseModel):
    name: str
    order: int = 0

class BoardColumnResponse(BoardColumnBase):
    id: str
    board_id: str
    tasks: List[BoardTaskResponse] = []
    class Config:
        from_attributes = True

class BoardBase(BaseModel):
    name: str
    description: Optional[str] = None

class BoardResponse(BoardBase):
    id: str
    created_at: datetime
    columns: List[BoardColumnResponse] = []
    epics: List[BoardEpicResponse] = []
    class Config:
        from_attributes = True
