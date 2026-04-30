from sqlalchemy import Column, String, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class Issue(Base):
    __tablename__ = "issues"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="OPEN") # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String, default="HIGH") # CRITICAL, HIGH, MEDIUM, LOW
    
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    assignee_name = Column(String, nullable=True)
    assignee_avatar = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
