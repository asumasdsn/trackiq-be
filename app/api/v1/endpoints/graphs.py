from fastapi import APIRouter
from app.schemas.graph import GraphRunRequest, GraphRunResponse, GraphStateResponse

router = APIRouter()


@router.post("/run", response_model=GraphRunResponse)
async def run_graph(payload: GraphRunRequest):
    """Invoke a LangGraph graph and return the final state."""
    pass


@router.post("/stream")
async def stream_graph(payload: GraphRunRequest):
    """Stream LangGraph graph events via Server-Sent Events."""
    pass


@router.get("/{thread_id}/state", response_model=GraphStateResponse)
async def get_graph_state(thread_id: str):
    """Retrieve the persisted state for a given thread."""
    pass


@router.delete("/{thread_id}/state", status_code=204)
async def clear_graph_state(thread_id: str):
    """Clear the checkpointed state for a thread."""
    pass
