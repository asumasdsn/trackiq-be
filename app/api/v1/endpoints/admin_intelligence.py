from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict
from datetime import datetime, timedelta
from app.core.database import get_db
from app.models.intelligence import IntelligenceLog
from pydantic import BaseModel

router = APIRouter()

class IntelligenceMetricResponse(BaseModel):
    total_triggers: int
    total_estimated_cost: float
    avg_execution_time: float
    triggers_by_day: List[Dict]
    top_models: List[Dict]

@router.get("/metrics", response_model=IntelligenceMetricResponse)
def get_intelligence_metrics(db: Session = Depends(get_db)):
    """Synthesize high-fidelity LLM observability metrics for the admin matrix."""
    
    # Total aggregations
    total_triggers = db.query(IntelligenceLog).count()
    total_cost = db.query(func.sum(IntelligenceLog.estimated_cost)).scalar() or 0.0
    avg_time = db.query(func.avg(IntelligenceLog.execution_time_ms)).scalar() or 0.0
    
    # Triggers by day (Last 7 days)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    day_metrics = db.query(
        func.date(IntelligenceLog.created_at).label("day"),
        func.count(IntelligenceLog.id).label("count"),
        func.sum(IntelligenceLog.estimated_cost).label("cost")
    ).filter(IntelligenceLog.created_at >= seven_days_ago)\
     .group_by(func.date(IntelligenceLog.created_at))\
     .order_by(func.date(IntelligenceLog.created_at)).all()
    
    triggers_by_day = [{"day": str(m.day), "count": m.count, "cost": float(m.cost or 0)} for m in day_metrics]
    
    # Top Models
    model_metrics = db.query(
        IntelligenceLog.model_name,
        func.count(IntelligenceLog.id).label("count")
    ).group_by(IntelligenceLog.model_name).all()
    
    top_models = [{"model": m.model_name, "count": m.count} for m in model_metrics]

    return IntelligenceMetricResponse(
        total_triggers=total_triggers,
        total_estimated_cost=total_cost,
        avg_execution_time=avg_time,
        triggers_by_day=triggers_by_day,
        top_models=top_models
    )

@router.get("/logs", response_model=List[Dict])
def get_recent_intelligence_logs(db: Session = Depends(get_db), limit: int = 50):
    """Retrieve the 50 most recent high-fidelity neural logs."""
    logs = db.query(IntelligenceLog).order_by(IntelligenceLog.created_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "task_type": l.task_type,
            "model": l.model_name,
            "cost": l.estimated_cost,
            "time": l.execution_time_ms,
            "created_at": l.created_at
        } for l in logs
    ]
