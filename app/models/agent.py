from sqlalchemy import Column, String, DateTime, JSON
from datetime import datetime
import uuid

from app.core.database import Base


class Agent(Base):
    __tablename__ = "agents"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    graph_id = Column(String, nullable=False)
    description = Column(String, nullable=True)
    config = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
