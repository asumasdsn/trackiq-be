from fastapi import APIRouter, HTTPException
from app.schemas.chat import ChatRequest, ChatResponse
from app.agents.prompt_agent.runner import PromptAgentRunner

router = APIRouter()
agent_runner = PromptAgentRunner()


@router.post("/", response_model=ChatResponse)
async def chat(payload: ChatRequest):
    """Send a message and get a response from the PromptAgent."""
    try:
        # Use a default thread_id if none provided
        thread_id = payload.thread_id or "default-thread"
        
        # Run the agent
        result = await agent_runner.run(
            {"messages": [{"role": "user", "content": payload.message}]}, 
            thread_id=thread_id
        )
        
        # The result of a LangGraph run depends on the state layout
        # Assuming the state has a 'messages' list with the last AI response
        last_message = result["messages"][-1]
        
        return ChatResponse(
            thread_id=thread_id,
            reply=last_message.content
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/stream")
async def stream_chat(payload: ChatRequest):
    """Stream tokens from the active agent via Server-Sent Events."""
    # Logic for SSE streaming would go here
    pass
