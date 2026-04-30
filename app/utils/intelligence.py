from sqlalchemy.orm import Session
from app.models.intelligence import IntelligenceLog
from typing import Optional

def log_intelligence_usage(
    db: Session,
    task_type: str,
    model_name: str,
    prompt_tokens: int = 0,
    completion_tokens: int = 0,
    execution_time_ms: Optional[int] = None,
    status: str = "SUCCESS"
):
    """Log an AI orchestration event with estimated cost calculation."""
    # Simple cost calculation: $0.002 per 1k tokens for local/small models (customizable)
    # Since it's local Ollama mostly, we might set cost to 0 or a nominal "infrastructure cost"
    estimated_cost = ((prompt_tokens + completion_tokens) / 1000) * 0.002
    
    log = IntelligenceLog(
        task_type=task_type,
        model_name=model_name,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        estimated_cost=estimated_cost,
        status=status,
        execution_time_ms=execution_time_ms
    )
    db.add(log)
    db.commit()
    return log
