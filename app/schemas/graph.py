from pydantic import BaseModel, Field
from typing import Any, Optional


class GraphRunRequest(BaseModel):
    graph_name: str = Field(..., description="Name of the compiled LangGraph graph")
    thread_id: Optional[str] = Field(None, description="Thread ID for stateful checkpointing")
    input: dict = Field(..., description="Initial input state for the graph")
    config: Optional[dict] = Field(default_factory=dict)


class GraphRunResponse(BaseModel):
    thread_id: str
    output: Any
    final_state: dict


class GraphStateResponse(BaseModel):
    thread_id: str
    state: dict
    checkpoint_id: Optional[str]
