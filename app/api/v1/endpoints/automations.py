from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List
import os
import httpx
import json
import io

from app.core.database import get_db
import json_repair
from app.models.automation import AutomationTask, AutomationFile, SystemPrompt
from app.models.project import Project
from app.models.project_board import Board, BoardColumn, BoardEpic, BoardTask
from app.schemas.automation import AutomationTaskResponse, AutomationTaskCreate, AutomationTaskUpdate
from fastapi.responses import Response

# Optional: PDF support
try:
    import pypdf
except ImportError:
    pypdf = None

router = APIRouter()


@router.post("/generate", response_model=List[AutomationTaskResponse])
async def generate_automations(
    prompt: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Parse project doc and break down into tasks using a local AI (Ollama) + json-repair."""

    file_id = None
    file_name = "User Prompt"
    file_content = ""
    if file:
        file_content_bytes = await file.read()
        file_name = file.filename
        
        # Save file to DB
        new_file = AutomationFile(
            filename=file.filename,
            content_type=file.content_type or "application/octet-stream",
            file_data=file_content_bytes
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        file_id = new_file.id

        # Extract text for AI
        if file.content_type == "application/pdf" and pypdf:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(file_content_bytes))
                file_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            except Exception as e:
                print(f"Error extracting PDF: {e}")
                file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]
        else:
            file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]

    # 1. Fetch System Prompt
    system_prompt_record = db.query(SystemPrompt).filter_by(name="Kanban Task Generator").first()
    if not system_prompt_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="System Prompt 'Kanban Task Generator' not found in database."
        )

    SYSTEM_PROMPT = system_prompt_record.content

    # 1.5 Fetch Available Employees with Project Names
    from app.models.employee import Employee
    from app.models.project import Project as ProjectModel
    employees = db.query(Employee).all()
    
    employee_data = []
    for e in employees:
        p_name = "Unassigned"
        if e.project_id:
            proj = db.query(ProjectModel).filter_by(id=e.project_id).first()
            if proj:
                p_name = proj.name
        employee_data.append(f"- {e.name} ({e.position}) [Project: {p_name}]")
    
    employee_list = "\n".join(employee_data)
    if not employee_list:
        employee_list = "No specific team members registered yet. Use generic roles."

    # 2. Local LLM call via Ollama
    ollama_url = os.getenv("OLLAMA_URL", "http://ollama:11434")
    model_name = os.getenv("LOCAL_MODEL", "phi3:latest")
    
    llm_raw = ""
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            response = await client.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system", 
                            "content": f"{SYSTEM_PROMPT}\n\nAVAILABLE TEAM & ALLOCATIONS:\n{employee_list}\n\nINSTRUCTION: Choose your 'project_name' first. Then, assign tasks ONLY to the names listed above. Match their 'Project' tag to your chosen 'project_name' if possible. If no one matches, pick from the 'Unassigned' pool."
                        },
                        {"role": "user", "content": f"User Prompt: {prompt}\n\nDocument Context: {file_content}"}
                    ],
                    "stream": False,
                    "format": "json"
                }
            )
            if response.status_code == 200:
                llm_raw = response.json().get("message", {}).get("content", "")
            else:
                print(f"Ollama error: {response.status_code}")
    except Exception as e:
        print(f"Ollama connection failed: {e}")

    # Fallback mock
    if not llm_raw:
        llm_raw = """
        {
            "project_name": "AI Orchestration Suite",
            "project_lead": "AI Agent",
            "tasks": [
                {
                    "title": "Configure local inference engine",
                    "identifier": "CORE-001",
                    "description": "Set up Ollama with GPU optimization for faster generation.",
                    "assignee_name": "Sarah Chen",
                    "assignee_avatar": "SC",
                    "epic": "ENDEAVOUR",
                    "column": "TO DO",
                    "labels": ["Infrastructure"]
                }
            ]
        }
        """

    # 3. Parse and Integrate
    parsed_data = json_repair.loads(llm_raw)
    
    # Ensure Project exists
    p_name = parsed_data.get("project_name", "AI Process Migration")
    p_lead = parsed_data.get("project_lead", "AI Management")
    
    project = db.query(Project).filter_by(name=p_name).first()
    if not project:
        project = Project(
            name=p_name,
            lead=p_lead,
            status="ON TRACK",
            status_color="bg-emerald-50 text-emerald-600 border-emerald-100",
            progress=0,
            automations_count=0
        )
        db.add(project)
        db.commit()
        db.refresh(project)

    # Ensure Board exists for this project
    board = db.query(Board).filter_by(project_id=project.id).first()
    if not board:
        board = Board(name=f"{p_name} Board", project_id=project.id)
        db.add(board)
        db.commit()
        db.refresh(board)
        
        # Create standard columns
        cols = [
            BoardColumn(board_id=board.id, name="TO DO", order=0),
            BoardColumn(board_id=board.id, name="IN PROGRESS", order=1),
            BoardColumn(board_id=board.id, name="QA", order=2),
            BoardColumn(board_id=board.id, name="DONE", order=3)
        ]
        db.add_all(cols)
        db.commit()

    # Refresh columns/epics maps
    col_map = {c.name.upper(): c.id for c in db.query(BoardColumn).filter_by(board_id=board.id).all()}
    epic_map = {e.name.upper(): e.id for e in db.query(BoardEpic).filter_by(board_id=board.id).all()}

    automation_tasks = []
    
    for tk in parsed_data.get("tasks", []):
        # Handle Column
        c_name = tk.get("column", "TO DO").upper()
        c_id = col_map.get(c_name) or col_map.get("TO DO")
        
        # Handle Epic (Create if missing)
        e_name = tk.get("epic", "GENERAL").upper()
        e_id = epic_map.get(e_name)
        if not e_id:
            new_epic = BoardEpic(board_id=board.id, name=e_name, color="bg-blue-50 text-blue-700")
            db.add(new_epic)
            db.commit()
            db.refresh(new_epic)
            e_id = new_epic.id
            epic_map[e_name] = e_id

        # Create Board Task
        bt = BoardTask(
            column_id=c_id,
            epic_id=e_id,
            title=tk.get("title"),
            description=tk.get("description"),
            assignee_name=tk.get("assignee_name"),
            assignee_avatar=tk.get("assignee_avatar"),
            identifier=tk.get("identifier"),
            labels=tk.get("labels", [])
        )
        db.add(bt)
        
        # Create Automation Record
        at = AutomationTask(
            title=f"Auto-pushed: {tk.get('identifier')}",
            priority="HIGH PRIORITY",
            tags=tk.get("labels", ["AI"]),
            assignee_name=tk.get("assignee_name", "System"),
            assignee_role="Developer",
            assignee_avatar=tk.get("assignee_avatar", "AI"),
            reason=f"Generated from '{file_name}' and automatically assigned to the '{p_name}' board.",
            border_color="border-blue-500",
            status="APPROVED",
            attached_file_id=file_id
        )
        db.add(at)
        automation_tasks.append(at)

    project.automations_count += len(automation_tasks)
    db.commit()
    
    for t in automation_tasks:
        db.refresh(t)
        
    return automation_tasks


@router.get("/files/{file_id}")
def download_file(file_id: str, db: Session = Depends(get_db)):
    db_file = db.query(AutomationFile).filter_by(id=file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return Response(content=db_file.file_data, media_type=db_file.content_type, headers={
        "Content-Disposition": f"attachment; filename={db_file.filename}"
    })


@router.get("/prompts")
def list_system_prompts(db: Session = Depends(get_db)):
    prompts = db.query(SystemPrompt).all()
    return [{"id": p.id, "title": p.name, "description": p.description, "content": p.content, "active": "Kanban" in p.name} for p in prompts]


@router.get("/", response_model=List[AutomationTaskResponse])
def get_automations(db: Session = Depends(get_db)):
    return db.query(AutomationTask).order_by(AutomationTask.created_at.desc()).all()


@router.post("/", response_model=AutomationTaskResponse, status_code=status.HTTP_201_CREATED)
def create_automation(task: AutomationTaskCreate, db: Session = Depends(get_db)):
    db_task = AutomationTask(**task.model_dump())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.patch("/{task_id}", response_model=AutomationTaskResponse)
def update_automation(task_id: str, task: AutomationTaskUpdate, db: Session = Depends(get_db)):
    db_task = db.query(AutomationTask).filter_by(id=task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.model_dump(exclude_unset=True).items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_automation(task_id: str, db: Session = Depends(get_db)):
    db_task = db.query(AutomationTask).filter_by(id=task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
