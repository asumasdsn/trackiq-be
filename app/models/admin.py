from sqlalchemy import Column, String, Boolean, DateTime, JSON, ForeignKey, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.core.database import Base

class SystemSettings(Base):
    __tablename__ = "system_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    key = Column(String, unique=True, index=True, nullable=False)
    value = Column(JSON, nullable=False)
    description = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=True)
    action = Column(String, nullable=False) # e.g., "USER_LOGIN", "SETTINGS_UPDATE"
    resource = Column(String, nullable=True) # e.g., "auth", "system_settings"
    details = Column(JSON, nullable=True)
    ip_address = Column(String, nullable=True)
    status = Column(String, default="SUCCESS") # SUCCESS, FAILED
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", backref="audit_logs")

class OrganizationProfile(Base):
    __tablename__ = "organization_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    industry = Column(String, nullable=True)
    address = Column(String, nullable=True)
    primary_contact_name = Column(String, nullable=True)
    primary_contact_email = Column(String, nullable=True)
    primary_contact_phone = Column(String, nullable=True)
    logo_url = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
