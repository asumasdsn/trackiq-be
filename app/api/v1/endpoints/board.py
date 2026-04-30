from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.project_board import Board, BoardColumn, BoardEpic, BoardTask, TaskComment
from app.schemas.project_board import BoardResponse, BoardTaskResponse, BoardTaskCreate

from app.utils.audit import log_audit

router = APIRouter()

@router.get("/", response_model=List[BoardResponse])
def get_boards(db: Session = Depends(get_db)):
    """Retrieve all boards with their columns and tasks."""
    return db.query(Board).all()

@router.get("/{board_id}", response_model=BoardResponse)
def get_board(board_id: str, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found")
    return board

@router.get("/project/{project_id}", response_model=BoardResponse)
def get_board_by_project(project_id: str, db: Session = Depends(get_db)):
    board = db.query(Board).filter(Board.project_id == project_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board not found for this project")
    return board

@router.post("/tasks", response_model=BoardTaskResponse)
def create_board_task(task: BoardTaskCreate, db: Session = Depends(get_db)):
    db_task = BoardTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    
    # Audit Log
    log_audit(db, action="TASK_CREATED", resource="board", details={"task_id": db_task.id, "title": db_task.title})
    
    return db_task

@router.delete("/tasks/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(BoardTask).filter(BoardTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Audit Log
    log_audit(db, action="TASK_DELETED", resource="board", details={"task_id": task_id, "title": db_task.title})
    
    db.delete(db_task)
    db.commit()
    return None

@router.get("/tasks/{task_id}", response_model=BoardTaskResponse)
def get_task_details(task_id: str, db: Session = Depends(get_db)):
    """Fetch all details for a single task including comments."""
    task = db.query(BoardTask).filter(BoardTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.post("/tasks/{task_id}/comments")
def add_task_comment(task_id: str, content: str, author_name: str, author_avatar: str, db: Session = Depends(get_db)):
    """Add a new comment to a task."""
    comment = TaskComment(
        task_id=task_id,
        content=content,
        author_name=author_name,
        author_avatar=author_avatar
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    
    # Audit Log
    db_task = db.query(BoardTask).filter(BoardTask.id == task_id).first()
    log_audit(db, action="COMMENT_ADDED", resource="board", details={"task_id": task_id, "task_title": db_task.title if db_task else "Unknown"})
    
    return comment

@router.patch("/tasks/{task_id}/move", response_model=BoardTaskResponse)
def move_task(task_id: str, column_id: str, db: Session = Depends(get_db)):
    db_task = db.query(BoardTask).filter(BoardTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    old_col_id = db_task.column_id
    db_task.column_id = column_id
    db.commit()
    db.refresh(db_task)
    
    # Audit Log
    target_col = db.query(BoardColumn).filter(BoardColumn.id == column_id).first()
    log_audit(
        db, 
        action="TASK_MOVED", 
        resource="board", 
        details={
            "task_id": task_id, 
            "title": db_task.title, 
            "to_column": target_col.name if target_col else "Unknown"
        }
    )
    
    return db_task

@router.patch("/tasks/{task_id}/vcs", response_model=BoardTaskResponse)
def update_task_vcs(task_id: str, github_data: dict, db: Session = Depends(get_db)):
    """Update GitHub/VCS metadata for a task."""
    db_task = db.query(BoardTask).filter(BoardTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    db_task.github_data = github_data
    db.commit()
    db.refresh(db_task)
    
    # Audit Log
    log_audit(db, action="TASK_VCS_LINKED", resource="board", details={"task_id": task_id, "branch": github_data.get("branch")})
    
    return db_task
