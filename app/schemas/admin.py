from pydantic import BaseModel
from typing import Optional, Any, List
from datetime import datetime

# System Settings Schemas
class SystemSettingsBase(BaseModel):
    key: str
    value: Any
    description: Optional[str] = None

class SystemSettingsCreate(SystemSettingsBase):
    pass

class SystemSettingsUpdate(BaseModel):
    value: Any
    description: Optional[str] = None

class SystemSettings(SystemSettingsBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogBase(BaseModel):
    action: str
    resource: Optional[str] = None
    details: Optional[Any] = None
    ip_address: Optional[str] = None
    status: str = "SUCCESS"

class AuditLog(AuditLogBase):
    id: str
    user_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Organization Profile Schemas
class OrganizationProfileBase(BaseModel):
    name: str
    industry: Optional[str] = None
    address: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    logo_url: Optional[str] = None

class OrganizationProfileUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    address: Optional[str] = None
    primary_contact_name: Optional[str] = None
    primary_contact_email: Optional[str] = None
    primary_contact_phone: Optional[str] = None
    logo_url: Optional[str] = None

class OrganizationProfile(OrganizationProfileBase):
    id: str
    updated_at: datetime

    class Config:
        from_attributes = True
