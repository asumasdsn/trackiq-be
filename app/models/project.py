from sqlalchemy import Column, String, Integer, DateTime, JSON
from datetime import datetime
import uuid

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    lead = Column(String, nullable=False)
    progress = Column(Integer, default=0)
    eta = Column(String, nullable=True)
    status = Column(String, default="ON TRACK")
    status_color = Column(String, nullable=True) # e.g. "bg-emerald-50 text-emerald-600 border-emerald-100"
    automations_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
