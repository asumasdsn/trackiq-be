from sqlalchemy.orm import Session
from app.models.admin import AuditLog
import json

def log_audit(
    db: Session,
    action: str,
    resource: str,
    user_id: str = None,
    details: dict = None,
    status: str = "SUCCESS",
    ip_address: str = None
):
    """Utility to record an action in the Audit Log table."""
    try:
        audit_entry = AuditLog(
            user_id=user_id,
            action=action,
            resource=resource,
            details=details,
            status=status,
            ip_address=ip_address
        )
        db.add(audit_entry)
        db.commit()
    except Exception as e:
        print(f"Failed to log audit activity: {e}")
        db.rollback()
