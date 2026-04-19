from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.project import ProjectCreate, ProjectResponse
from app.models.project import Project
from app.core.database import get_db

router = APIRouter()


@router.get("/", response_model=list[ProjectResponse])
async def list_projects(db: Session = Depends(get_db)):
    return db.query(Project).all()


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    project = Project(**payload.model_dump())
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
async def update_project(project_id: str, payload: dict, db: Session = Depends(get_db)):
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    
    for key, value in payload.items():
        setattr(project, key, value)
    
    db.commit()
    db.refresh(project)
    return project
