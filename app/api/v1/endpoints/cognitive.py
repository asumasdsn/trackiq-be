from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os
import httpx
import json
from pydantic import BaseModel

from app.core.database import get_db
from app.models.project import Project
from app.models.project_board import BoardTask, BoardColumn

router = APIRouter()

class ProjectSummaryRequest(BaseModel):
    project_id: str

class ProjectSummaryResponse(BaseModel):
    summary: str
    status_trend: str # Improving, Stagnant, At Risk
    key_insight: str

@router.post("/summarize-project", response_model=ProjectSummaryResponse)
async def summarize_project(req: ProjectSummaryRequest, db: Session = Depends(get_db)):
    """Generate a GenAI-driven intelligence summary for a specific project node."""
    project = db.query(Project).filter_by(id=req.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project node not found.")

    tasks = db.query(BoardTask).join(BoardColumn).filter(BoardColumn.board_id.has(project_id=project.id)).all()
    task_metadata = [f"Task: {t.title} | Status: {t.column.name if t.column else 'Unk'} | Priority: {t.priority}" for t in tasks[:20]]
    context = "\n".join(task_metadata)

    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("LOCAL_MODEL", "phi3:latest")
    
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            response = await client.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system", 
                            "content": "Analyze project data and provide a concise summary, trend, and ONE key architectural insight. Output JSON: {\"summary\": \"...\", \"status_trend\": \"...\", \"key_insight\": \"...\"}"
                        },
                        {"role": "user", "content": f"Project: {project.name}\n\nTasks:\n{context}"}
                    ],
                    "stream": False, "format": "json"
                }
            )
            data = json.loads(response.json().get("message", {}).get("content", ""))
            return ProjectSummaryResponse(**data)
    except:
        return ProjectSummaryResponse(summary="Neural link unstable. Manual audit required.", status_trend="Stable", key_insight="Check sync.")

class CommandRequest(BaseModel):
    query: str
    current_path: str

class CommandResponse(BaseModel):
    action: str 
    param: str
    message: str

@router.post("/execute-command", response_model=CommandResponse)
async def execute_command(req: CommandRequest, db: Session = Depends(get_db)):
    """Parse natural language command and return the strategic platform action."""
    q = req.query.lower()
    
    # Heuristic shortcuts
    if "board" in q: return CommandResponse(action="NAVIGATE", param="/dashboard/boards", message="Redirecting to Board Matrix...")
    if "automation" in q: return CommandResponse(action="NAVIGATE", param="/dashboard/automation", message="Entering Automation Hub...")
    if "employee" in q: return CommandResponse(action="NAVIGATE", param="/dashboard/employees", message="Syncing personnel nodes...")
    if "portfolio" in q: return CommandResponse(action="NAVIGATE", param="/dashboard/portfolio", message="Mapping Global Portfolio...")

    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("LOCAL_MODEL", "phi3:latest")
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {"role": "system", "content": "Extract target intent: [PORTFOLIO, BOARDS, EMPLOYEES, AUTOMATION]. Output JSON: {\"target\": \"...\"}"},
                        {"role": "user", "content": f"Command: {req.query}"}
                    ],
                    "stream": False, "format": "json"
                }
            )
            target = json.loads(response.json()["message"]["content"])["target"]
            path_map = {"PORTFOLIO": "/dashboard/portfolio", "BOARDS": "/dashboard/boards", "EMPLOYEES": "/dashboard/employees", "AUTOMATION": "/dashboard/automation"}
            return CommandResponse(action="NAVIGATE", param=path_map.get(target, "/dashboard/portfolio"), message="Intent resolved.")
    except:
        return CommandResponse(action="SEARCH", param=req.query, message="Neural link weak. Standard search activated.")
