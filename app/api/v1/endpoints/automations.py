from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.automation import AutomationTask
from app.schemas.automation import AutomationTaskResponse, AutomationTaskCreate, AutomationTaskUpdate

router = APIRouter()

@router.get("/", response_model=List[AutomationTaskResponse])
def get_automations(db: Session = Depends(get_db)):
    """Retrieve all automation tasks."""
    return db.query(AutomationTask).order_by(AutomationTask.created_at.desc()).all()

@router.post("/", response_model=AutomationTaskResponse, status_code=status.HTTP_201_CREATED)
def create_automation(task: AutomationTaskCreate, db: Session = Depends(get_db)):
    """Create a new automation task."""
    db_task = AutomationTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.patch("/{task_id}", response_model=AutomationTaskResponse)
def update_automation(task_id: str, task: AutomationTaskUpdate, db: Session = Depends(get_db)):
    """Update an automation task partially."""
    db_task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    update_data = task.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_task, key, value)
        
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_automation(task_id: str, db: Session = Depends(get_db)):
    """Delete an automation task."""
    db_task = db.query(AutomationTask).filter(AutomationTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
        
    db.delete(db_task)
    db.commit()
