from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    position: str
    email: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(BaseModel):
    name: Optional[str] = None
    position: Optional[str] = None
    email: Optional[str] = None
    project_id: Optional[str] = None
    project_name: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: str

    class Config:
        from_attributes = True
