from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.agent import AgentCreateRequest, AgentResponse
from app.services.agent_service import AgentService
from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=list[AgentResponse])
async def list_agents(db: Session = Depends(get_db)):
    """List all registered LangGraph agents."""
    service = AgentService(db)
    return service.list_agents()


@router.post("/", response_model=AgentResponse, status_code=201)
async def create_agent(payload: AgentCreateRequest, db: Session = Depends(get_db)):
    """Register a new agent configuration."""
    service = AgentService(db)
    return service.create_agent(payload)


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(agent_id: str, db: Session = Depends(get_db)):
    """Retrieve a single agent by ID."""
    service = AgentService(db)
    agent = service.get_agent(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.delete("/{agent_id}", status_code=204)
async def delete_agent(agent_id: str, db: Session = Depends(get_db)):
    """Remove an agent registration."""
    service = AgentService(db)
    service.delete_agent(agent_id)
    return None


@router.patch("/{agent_id}", response_model=AgentResponse)
async def update_agent(agent_id: str, payload: dict, db: Session = Depends(get_db)):
    """Update an existing agent configuration."""
    service = AgentService(db)
    agent = service.update_agent(agent_id, payload)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent
