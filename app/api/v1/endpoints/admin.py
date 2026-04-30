from typing import List, Any
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
import uuid

from app.core.database import get_db
from app.models.admin import SystemSettings, AuditLog, OrganizationProfile, PermissionModule
from app.models.user import User
from app.schemas import admin as admin_schemas
from app.core.deps import get_current_super_admin

router = APIRouter()

# --- System Settings & Feature Flags ---

@router.get("/features")
def get_features(db: Session = Depends(get_db)):
    """Retrieve all feature flags from the system nodes."""
    settings = db.query(SystemSettings).filter(SystemSettings.key.like("feature_%")).all()
    defaults = {
        "feature_live_clock": True,
        "feature_notifications": True,
        "feature_ai_generation": True
    }
    
    result = {**defaults}
    for s in settings:
        result[s.key] = s.value.get("enabled", True) if isinstance(s.value, dict) else s.value
        
    return result

@router.post("/features/toggle/{key}")
def toggle_feature(key: str, enabled: bool, db: Session = Depends(get_db)):
    """Orchestrate a specific feature flag toggle."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == key).first()
    if setting:
        setting.value = {"enabled": enabled}
    else:
        setting = SystemSettings(key=key, value={"enabled": enabled}, description=f"Feature flag for {key}")
        db.add(setting)
    
    db.commit()
    return {"key": key, "enabled": enabled}

@router.get("/config", response_model=List[admin_schemas.SystemSettings])
def get_all_settings(db: Session = Depends(get_db)):
    """Retrieve all global configuration nodes."""
    return db.query(SystemSettings).all()

@router.post("/config")
def update_system_setting(setting_in: admin_schemas.SystemSettingsCreate, db: Session = Depends(get_db)):
    """Update or create a global system setting node."""
    setting = db.query(SystemSettings).filter(SystemSettings.key == setting_in.key).first()
    if setting:
        setting.value = setting_in.value
        if setting_in.description:
            setting.description = setting_in.description
    else:
        setting = SystemSettings(**setting_in.model_dump())
        db.add(setting)
    
    db.commit()
    db.refresh(setting)
    return setting

# --- Organization Profile ---

@router.get("/profile", response_model=admin_schemas.OrganizationProfile)
def get_organization_profile(db: Session = Depends(get_db)):
    """Retrieve the consolidated organization profile node."""
    profile = db.query(OrganizationProfile).first()
    if not profile:
        profile = OrganizationProfile(name="TrackIQ Enterprise Node")
        db.add(profile)
        db.commit()
        db.refresh(profile)
    return profile

@router.patch("/profile", response_model=admin_schemas.OrganizationProfile)
def update_organization_profile(
    profile_in: admin_schemas.OrganizationProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update organization profile parameters."""
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

# --- Permission Matrix Modules ---

@router.get("/permissions/modules")
def list_permission_modules(db: Session = Depends(get_db)):
    """Retrieve all high-fidelity permission matrix modules."""
    # Convert to dict manually to avoid Pydantic ORM serialization issues
    modules = db.query(PermissionModule).order_by(PermissionModule.category).all()
    return [
        {
            "id": m.id,
            "name": m.name,
            "description": m.description,
            "icon_name": m.icon_name,
            "default_permissions": m.default_permissions,
            "category": m.category,
            "created_at": m.created_at
        } for m in modules
    ]

@router.post("/permissions/modules")
def create_permission_module(module: dict, db: Session = Depends(get_db)):
    """Inject a new permission module node into the matrix."""
    db_module = PermissionModule(**module)
    db.add(db_module)
    db.commit()
    db.refresh(db_module)
    return db_module

# --- Audit Logs ---

@router.get("/logs", response_model=List[admin_schemas.AuditLog])
def get_audit_logs(limit: int = 100, skip: int = 0, db: Session = Depends(get_db)):
    """View system-wide audit telemetry."""
    return db.query(AuditLog).order_by(AuditLog.created_at.desc()).offset(skip).limit(limit).all()

# --- User & Permissions Management ---

@router.get("/users")
def list_system_users(db: Session = Depends(get_db)):
    """List all personnel nodes for access management."""
    users = db.query(User).all()
    # Explicitly serialize to avoid ORM type issues
    return [
        {
            "id": u.id,
            "full_name": u.full_name,
            "email": u.email,
            "is_super_admin": u.is_super_admin,
            "is_active": u.is_active,
            "avatar_url": u.avatar_url
        } for u in users
    ]

@router.patch("/users/{user_id}/permissions")
def update_user_permissions(
    user_id: str,
    is_super_admin: bool,
    is_active: bool,
    db: Session = Depends(get_db)
):
    """Reconfigure user access parameters."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_super_admin = is_super_admin
    user.is_active = is_active
    db.commit()
    return {"message": "Personnel permissions updated successfully"}
