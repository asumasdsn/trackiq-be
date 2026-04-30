from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship
import uuid
from app.core.database import Base

class Employee(Base):
    __tablename__ = "employees"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()), index=True)
    name = Column(String, nullable=False)
    position = Column(String, nullable=False) # e.g. Frontend Developer, Senior DevOps
    email = Column(String, nullable=True)
    project_id = Column(String, ForeignKey("projects.id"), nullable=True)
    project_name = Column(String, nullable=True) # For manual entry or cache
    
    project = relationship("Project", backref="team_members")
