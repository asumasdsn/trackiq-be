from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class AutomationTask(Base):
    __tablename__ = "automation_tasks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    title = Column(String, nullable=False)
    priority = Column(String, nullable=False) # HIGH PRIORITY, STANDARD, CRITICAL
    tags = Column(JSON, default=list) # Array of strings
    assignee_name = Column(String, nullable=False)
    assignee_role = Column(String, nullable=False)
    assignee_avatar = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    border_color = Column(String, nullable=False) # e.g. border-blue-600
    full_width = Column(Boolean, default=False)
    status = Column(String, default="PENDING") # PENDING, APPROVED, REJECTED
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
