from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.issue import Issue
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()

class IssueBase(BaseModel):
    title: str
    description: str = ""
    status: str = "OPEN"
    priority: str = "HIGH"
    project_id: str = None
    assignee_name: str = None
    assignee_avatar: str = None

class IssueResponse(IssueBase):
    id: str
    created_at: datetime
    
    class Config:
        from_attributes = True

@router.get("/", response_model=List[IssueResponse])
def list_issues(db: Session = Depends(get_db)):
    """Retrieve all issue nodes from the strategic matrix."""
    return db.query(Issue).order_by(Issue.created_at.desc()).all()

@router.post("/", response_model=IssueResponse, status_code=status.HTTP_201_CREATED)
def create_issue(issue: IssueBase, db: Session = Depends(get_db)):
    """Inject a new issue node into the matrix."""
    db_issue = Issue(**issue.model_dump())
    db.add(db_issue)
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.patch("/{issue_id}", response_model=IssueResponse)
def update_issue(issue_id: str, issue: dict, db: Session = Depends(get_db)):
    """Update an existing issue's parameters."""
    db_issue = db.query(Issue).filter_by(id=issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue node not found.")
    
    for key, value in issue.items():
        if hasattr(db_issue, key):
            setattr(db_issue, key, value)
            
    db.commit()
    db.refresh(db_issue)
    return db_issue

@router.delete("/{issue_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_issue(issue_id: str, db: Session = Depends(get_db)):
    """Neural termination of an issue node."""
    db_issue = db.query(Issue).filter_by(id=issue_id).first()
    if not db_issue:
        raise HTTPException(status_code=404, detail="Issue node not found.")
    db.delete(db_issue)
    db.commit()
