from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter()


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Send a message and get a response from the active LangGraph agent."""
    pass


@router.post("/stream")
async def stream_chat(payload: ChatRequest):
    """Stream tokens from the active agent via Server-Sent Events."""
    pass


@router.get("/{thread_id}/history")
async def get_chat_history(thread_id: str):
    """Return the message history for a thread."""
    pass
