from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.admin import SystemSettings, AuditLog, OrganizationProfile
from app.models.user import User
from app.schemas import admin as admin_schemas
from app.core.deps import get_current_super_admin

router = APIRouter()

# --- System Settings ---

@router.get("/config", response_model=List[admin_schemas.SystemSettings])
def get_all_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Retrieve all system-wide settings."""
    return db.query(SystemSettings).all()

@router.post("/config", response_model=admin_schemas.SystemSettings)
def create_or_update_setting(
    setting_in: admin_schemas.SystemSettingsCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Create or update a system setting."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == setting_in.key).first()
    if setting:
        setting.value = setting_in.value
        setting.description = setting_in.description
    else:
        setting = SystemSettings(**setting_in.model_dump())
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting

# --- Organization Profile ---

@router.get("/profile", response_model=admin_schemas.OrganizationProfile)
def get_organization_profile(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Retrieve the organization profile settings."""
    profile = db.query(OrganizationProfile).first()
    if not profile:
        # Create a default one if it doesn't exist
        profile = OrganizationProfile(name="TrackIQ Organization")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.patch("/profile", response_model=admin_schemas.OrganizationProfile)
def update_organization_profile(
    profile_in: admin_schemas.OrganizationProfileUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Update organization profile details."""
    profile = db.query(OrganizationProfile).first()
    if not profile:
        profile = OrganizationProfile(**profile_in.model_dump(exclude_unset=True))
        db.add(profile)
    else:
        obj_data = profile_in.model_dump(exclude_unset=True)
        for key, value in obj_data.items():
            setattr(profile, key, value)
    
    db.commit()
    db.refresh(profile)
    return profile

# --- Audit Logs ---

@router.get("/logs", response_model=List[admin_schemas.AuditLog])
def get_audit_logs(
    limit: int = 100,
    skip: int = 0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """View system audit logs."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

# --- User & Permissions Management ---

@router.get("/users", response_model=List[Any]) # Use a generic list for now or define a schema
def list_system_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """List all users in the system for admin management."""
    return db.query(User).all()

@router.patch("/users/{user_id}/permissions")
def update_user_permissions(
    user_id: str,
    is_super_admin: bool,
    is_active: bool,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_super_admin)
):
    """Toggle super-admin status or account activation for a user."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_super_admin = is_super_admin
    user.is_active = is_active
    db.commit()
    return {"message": "User permissions updated successfully"}
