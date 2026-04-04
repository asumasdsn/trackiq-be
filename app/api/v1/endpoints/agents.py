from fastapi import APIRouter, Depends
from app.schemas.agent import AgentCreateRequest, AgentResponse
from app.services.agent_service import AgentService

router = APIRouter()


@router.get("/", response_model=list[AgentResponse])
async def list_agents():
    """List all registered LangGraph agents."""
    pass


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(payload: AgentCreateRequest):
    """Register a new agent configuration."""
    pass


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str):
    """Retrieve a single agent by ID."""
    pass


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str):
    """Remove an agent registration."""
    pass
