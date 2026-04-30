from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
import os
import httpx
import json
import io
import asyncio
from fastapi.responses import StreamingResponse, Response
from pydantic import BaseModel

from app.core.database import get_db
import json_repair
from app.models.automation import AutomationTask, AutomationFile, SystemPrompt
from app.models.project import Project
from app.models.project_board import Board, BoardColumn, BoardEpic, BoardTask
from app.schemas.automation import AutomationTaskResponse, AutomationTaskCreate, AutomationTaskUpdate
from app.core.telemetry import telemetry
from app.utils.intelligence import log_intelligence_usage

# PDF support
try:
    import pypdf
except ImportError:
    pypdf = None

router = APIRouter()

class InterrogationResponse(BaseModel):
    questions: List[str]

@router.get("/telemetry")
async def stream_telemetry():
    """Server-Sent Events endpoint for real-time neural telemetry."""
    return StreamingResponse(
        telemetry.subscribe(),
        media_type="text/event-stream"
    )

@router.post("/interrogate", response_model=InterrogationResponse)
async def interrogate_intent(
    prompt: str = Form(...),
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Analyze prompt/file and generate 3 clarifying questions before plan synthesis."""
    
    await telemetry.emit("INFO", "Initializing Neural Interrogation sequence...")
    
    file_content = ""
    if file:
        await telemetry.emit("INFO", f"Deep-Scanning Artifact: {file.filename}")
        file_content_bytes = await file.read()
        if file.content_type == "application/pdf" and pypdf:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(file_content_bytes))
                file_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            except:
                file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]
        else:
            file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]

    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("LOCAL_MODEL", "phi3:latest")
    
    await telemetry.emit("AI_CORE", "Synthesizing strategic queries for intent validation...")
    
    try:
        async with httpx.AsyncClient(timeout=150.0) as client:
            response = await client.post(
                f"{ollama_url}/api/chat",
                json={
                    "model": model_name,
                    "messages": [
                        {
                            "role": "system", 
                            "content": "You are a Strategic Project Architect. Given a project brief, generate EXACTLY 3 clarifying questions that will help you create a more precise and customized project plan. Your goal is to maximize clarity on scope, technology, and deadlines. Output in RAW JSON: {\"questions\": [\"q1\", \"q2\", \"q3\"]}"
                        },
                        {"role": "user", "content": f"Brief: {prompt}\n\nContext: {file_content}"}
                    ],
                    "stream": False,
                    "format": "json"
                }
            )
            if response.status_code == 200:
                raw = response.json().get("message", {}).get("content", "")
                parsed = json_repair.loads(raw)
                await telemetry.emit("SUCCESS", "Interrogation logic compiled. 3 strategic nodes identified.")
                return InterrogationResponse(questions=parsed.get("questions", ["Describe the target architecture.", "What is the priority level for the first phase?", "Are there specific resource constraints?"]))
    except Exception as e:
        await telemetry.emit("ERROR", f"Interrogation Delay: Using fallback queries.")
        return InterrogationResponse(questions=[
            "What is the primary technical milestone for this initiative?",
            "Are there any specific resource constraints we should map to?",
            "What is the target deployment environment for these tasks?"
        ])

@router.post("/generate", response_model=List[AutomationTaskResponse])
async def generate_automations(
    prompt: str = Form(...),
    clarifications: str = Form(""), # JSON string of answers [{"q": "...", "a": "..."}]
    file: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    """Refined task generation including clarified user intent."""
    
    await telemetry.emit("INFO", "Synthesizing customized operational plan...")
    
    file_id = None
    file_name = "User Prompt"
    file_content = ""
    if file:
        file_content_bytes = await file.read()
        file_name = file.filename
        new_file = AutomationFile(filename=file.filename, content_type=file.content_type or "application/octet-stream", file_data=file_content_bytes)
        db.add(new_file)
        db.commit()
        db.refresh(new_file)
        file_id = new_file.id
        if file.content_type == "application/pdf" and pypdf:
            try:
                pdf_reader = pypdf.PdfReader(io.BytesIO(file_content_bytes))
                file_content = "\n".join([page.extract_text() for page in pdf_reader.pages])
            except:
                file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]
        else:
            file_content = file_content_bytes.decode("utf-8", errors="ignore")[:5000]

    system_prompt_record = db.query(SystemPrompt).filter_by(name="Kanban Task Generator").first()
    SYSTEM_PROMPT = system_prompt_record.content if system_prompt_record else "Generate Kanban tasks."

    from app.models.employee import Employee
    employees = db.query(Employee).all()
    employee_list = "\n".join([f"- {e.name} | Role: {e.position} | Active Project: {e.project_name or 'Unassigned'}" for e in employees])
    
    # Process clarifications
    clarified_context = ""
    if clarifications:
        try:
            answers = json.loads(clarifications)
            clarified_context = "\n\nSTRATEGIC CLARIFICATIONS (USER ANSWERS):\n" + "\n".join([f"Q: {a['q']}\nA: {a['a']}" for a in answers])
            await telemetry.emit("INFO", "Contextual answers integrated into neural pulse.")
        except:
            pass

    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    model_name = os.getenv("LOCAL_MODEL", "phi3:latest")
    
    await telemetry.emit("AI_CORE", "Executing custom plan synthesis with validated intent...")
    
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
                            "content": f"{SYSTEM_PROMPT}\n\nPERSONNEL:\n{employee_list}\n{clarified_context}"
                        },
                        {"role": "user", "content": f"User Prompt: {prompt}\n\nContext: {file_content}"}
                    ],
                    "stream": False,
                    "format": "json"
                }
            )
            llm_raw = response.json().get("message", {}).get("content", "")
            
            # Neural Observability: Log Usage
            log_intelligence_usage(
                db=db, task_type="GENERATE", model_name=model_name,
                prompt_tokens=len(prompt) // 4, # Fallback token estimation
                completion_tokens=len(llm_raw) // 4,
                status="SUCCESS"
            )
    except Exception as e:
        await telemetry.emit("ERROR", f"Local AI Link Failure: {str(e)}")

    parsed_data = json_repair.loads(llm_raw)
    
    # High-Resilience Refinement: Handle non-dictionary AI responses
    if not isinstance(parsed_data, dict):
        await telemetry.emit("WARNING", "Neural Synthesis provided a non-standard packet. Wrapping intent...")
        parsed_data = {
            "project_name": "AI Process Migration",
            "project_lead": "AI Management",
            "tasks": [{"title": str(parsed_data), "description": "Generated from unstructured neural pulse.", "column": "TO DO"}]
        }

    ai_project_name = parsed_data.get("project_name", "Custom Integration")
    
    project = db.query(Project).filter(Project.name.ilike(f"%{ai_project_name}%")).first()
    if not project:
        project = Project(name=ai_project_name, lead=parsed_data.get("project_lead", "Automation Eng"), status="ON TRACK", status_color="bg-emerald-50 text-emerald-600 border-emerald-100", progress=0, automations_count=0)
        db.add(project)
        db.commit()
        db.refresh(project)

    board = db.query(Board).filter_by(project_id=project.id).first()
    if not board:
        board = Board(name=f"{project.name} Board", project_id=project.id)
        db.add(board)
        db.commit()
        db.refresh(board)
        cols = [BoardColumn(board_id=board.id, name=n, order=i) for i, n in enumerate(["TO DO", "IN PROGRESS", "QA", "DONE"])]
        db.add_all(cols)
        db.commit()

    col_map = {c.name.upper(): c.id for c in db.query(BoardColumn).filter_by(board_id=board.id).all()}
    epic_map = {e.name.upper(): e.id for e in db.query(BoardEpic).filter_by(board_id=board.id).all()}

    automation_tasks = []
    for tk in parsed_data.get("tasks", []):
        c_name = tk.get("column", "TO DO").upper()
        c_id = col_map.get(c_name) or col_map.get("TO DO")
        e_name = tk.get("epic", "GENERAL").upper()
        e_id = epic_map.get(e_name)
        if not e_id:
            new_epic = BoardEpic(board_id=board.id, name=e_name, color="bg-blue-50 text-blue-700")
            db.add(new_epic)
            db.commit()
            db.refresh(new_epic)
            e_id = new_epic.id
            epic_map[e_name] = e_id

        bt = BoardTask(
            column_id=c_id, epic_id=e_id, title=tk.get("title", "Task Node"), 
            description=tk.get("description", ""), assignee_name=tk.get("assignee_name", "SA"),
            assignee_avatar=tk.get("assignee_avatar", "SA"), identifier=tk.get("identifier", "AUTO"),
            labels=tk.get("labels", [])
        )
        db.add(bt)
        at = AutomationTask(
            title=f"Auto-pushed: {bt.identifier}", priority="HIGH PRIORITY", tags=tk.get("labels", ["AI"]),
            assignee_name=bt.assignee_name, assignee_role="Developer", assignee_avatar=bt.assignee_avatar,
            reason=f"Custom plan synthesized from brief. Project: {project.name}",
            border_color="border-blue-500", status="APPROVED", attached_file_id=file_id,
            clarifications=answers if 'answers' in locals() else None
        )
        db.add(at)
        automation_tasks.append(at)

    project.automations_count += len(automation_tasks)
    db.commit()
    await telemetry.emit("SUCCESS", "Neural Generation Complete. Operational plan synchronized.")
    return [AutomationTaskResponse.model_validate(t) for t in automation_tasks]

@router.get("/files/{file_id}")
def download_file(file_id: str, db: Session = Depends(get_db)):
    db_file = db.query(AutomationFile).filter_by(id=file_id).first()
    if not db_file:
        raise HTTPException(status_code=404, detail="File not found")
    return Response(content=db_file.file_data, media_type=db_file.content_type, headers={"Content-Disposition": f"attachment; filename={db_file.filename}"})

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
