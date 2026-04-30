from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.core.database import get_db
from app.models.admin import AuditLog
from pydantic import BaseModel

router = APIRouter()

class NotificationResponse(BaseModel):
    id: str
    action: str
    resource: str
    details: dict | None
    created_at: datetime
    status: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[NotificationResponse])
def get_notifications(db: Session = Depends(get_db), limit: int = 10):
    """Fetch the most recent audit logs to serve as notifications."""
    logs = db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).all()
    return logs

@router.post("/clear")
def clear_notifications():
    """Placeholder for clearing notifications logic."""
    return {"message": "Notifications cleared"}
