from pydantic import BaseModel
from typing import Optional

class EmployeeBase(BaseModel):
    name: str
    position: str
    project_id: Optional[str] = None

class EmployeeCreate(EmployeeBase):
    pass

class EmployeeUpdate(EmployeeBase):
    name: Optional[str] = None
    position: Optional[str] = None

class EmployeeResponse(EmployeeBase):
    id: str

    class Config:
        from_attributes = True
