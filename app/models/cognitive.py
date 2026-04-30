from sqlalchemy import Column, String, JSON, Integer, Float, DateTime
from app.core.database import Base
from datetime import datetime

class PromptMapping(Base):
    __tablename__ = "prompt_mappings"

    id = Column(Integer, primary_key=True, index=True)
    user_prompt = Column(String, index=True)
    predicted_stage = Column(String)
    context_tags = Column(JSON) # e.g. ["frontend", "react"]
    success_score = Column(Float, default=1.0) # Strength of the mapping
    usage_count = Column(Integer, default=1)
    last_used = Column(DateTime, default=datetime.utcnow)

class CognitiveMemory(Base):
    __tablename__ = "cognitive_memory"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    value = Column(JSON)
    description = Column(String)
