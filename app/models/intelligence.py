from sqlalchemy import Column, String, DateTime, Integer, Float, Text
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class IntelligenceLog(Base):
    __tablename__ = "intelligence_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    task_type = Column(String, nullable=False) # GENERATE, SUMMARIZE, INTERROGATE, COMMAND
    model_name = Column(String, nullable=False)
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0)
    
    status = Column(String, default="SUCCESS")
    execution_time_ms = Column(Integer, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
