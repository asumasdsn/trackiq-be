from pydantic import BaseModel
from typing import Optional, List


class ToolResponse(BaseModel):
    name: str
    description: str
    parameters: Optional[dict] = None
    tags: Optional[List[str]] = None
