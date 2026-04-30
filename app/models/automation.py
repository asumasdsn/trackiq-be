from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, JSON, LargeBinary
from sqlalchemy.sql import func
from app.core.database import Base
import uuid
from datetime import datetime

class AutomationFile(Base):
    __tablename__ = "automation_files"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    filename = Column(String, nullable=False)
    content_type = Column(String, nullable=False)
    file_data = Column(LargeBinary, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class SystemPrompt(Base):
    __tablename__ = "system_prompts"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, unique=True, index=True, nullable=False)
    content = Column(String, nullable=False)
    description = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

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
    attached_file_id = Column(String, nullable=True)
    clarifications = Column(JSON, nullable=True) # Strategic interrogation Q&A
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
