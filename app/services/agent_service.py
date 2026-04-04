from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreateRequest


class AgentService:
    def __init__(self, db: Session):
        self.db = db

    def get_agent(self, agent_id: str):
        return self.db.query(Agent).filter(Agent.id == agent_id).first()

    def list_agents(self):
        return self.db.query(Agent).all()

    def create_agent(self, data: AgentCreateRequest):
        db_agent = Agent(
            name=data.name,
            graph_id=data.graph_id,
            description=data.description,
            config=data.config
        )
        self.db.add(db_agent)
        self.db.commit()
        self.db.refresh(db_agent)
        return db_agent

    def delete_agent(self, agent_id: str):
        agent = self.get_agent(agent_id)
        if agent:
            self.db.delete(agent)
            self.db.commit()
        return agent
