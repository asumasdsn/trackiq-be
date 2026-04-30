from sqlalchemy import inspect, text
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.admin import SystemSettings, AuditLog, OrganizationProfile
from app.models.project import Project
from app.models.automation import AutomationTask
from app.models.project_board import Board, BoardColumn, BoardEpic, BoardTask, TaskComment
from app.core.security import hash_password

def init_db():
    # 1. Create all missing tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Check for missing columns in existing tables (Self-healing)
    inspector = inspect(engine)
    
    try:
        columns = [c['name'] for c in inspector.get_columns("users")]
        if "is_super_admin" not in columns:
            print("Migrating: Adding 'is_super_admin' column to 'users' table")
            with engine.connect() as conn:
                conn.execute(text("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE"))
                conn.commit()
    except Exception as e:
        print(f"Non-critical migration notice (users): {e}")

    try:
        if "automation_tasks" in inspector.get_table_names():
            automation_columns = [c['name'] for c in inspector.get_columns("automation_tasks")]
            if "attached_file_id" not in automation_columns:
                print("Migrating: Adding 'attached_file_id' column to 'automation_tasks' table")
                with engine.connect() as conn:
                    conn.execute(text("ALTER TABLE automation_tasks ADD COLUMN attached_file_id VARCHAR"))
                    conn.commit()
    except Exception as e:
        print(f"Non-critical migration notice (automation_tasks): {e}")

    db = SessionLocal()
    try:
        # 3. Seed System Prompt (Universal)
        from app.models.automation import SystemPrompt
        if not db.query(SystemPrompt).filter_by(name="Kanban Task Generator").first():
            print("Seeding: Creating System Prompt")
            prompt = SystemPrompt(
                name="Kanban Task Generator",
                description="Prompt used to generate tasks from project files.",
                content='''You are an expert technical project manager AI. Your task is to analyze the provided project documentation and break it down into actionable tasks for a Kanban tracking board.
    
You must output your response EXACTLY as a JSON object matching this schema. Do not enclose it in markdown blocks (no ```json). Output only valid JSON.

{
    "tasks": [
        {
            "title": "Clear, concise task title",
            "identifier": "Short alphanumeric ID (e.g., FRONT-101)",
            "description": "Detailed explanation of the requirements",
            "assignee_name": "Suggested team member name based on their role",
            "assignee_avatar": "2 letter initials of assignee (e.g., SC)",
            "epic": "The broader category, e.g., ENDEAVOUR, EXPERIENCE",
            "column": "One of exactly: TO DO, IN PROGRESS, QA, DONE",
            "labels": ["string", "string"]
        }
    ]
}

Analyze the user's prompt or uploaded text, assess the required roles, and intelligently distribute the tasks across the team. Make sure to generate realistic assignments.'''
            )
            db.add(prompt)
            db.commit()

        # 4. Seed initial projects
        if not db.query(Project).first():
            print("Seeding: Creating initial projects")
            projects = [
                Project(name="Nexus Core Migration", lead="Sarah Jenkins", progress=78, eta="EST. 12 DAYS LEFT", status="ON TRACK", status_color="bg-emerald-50 text-emerald-600 border-emerald-100", automations_count=14),
                Project(name="Sentinel Data Purge", lead="Marcus Chen", progress=42, eta="DELAYED +4D", status="AT RISK", status_color="bg-amber-50 text-amber-600 border-amber-100", automations_count=8),
                Project(name="Project Alpha Launch", lead="Elena Rodriguez", progress=15, eta="PHASE: DISCOVERY", status="DELAYED", status_color="bg-slate-100 text-slate-600 border-slate-200", automations_count=3)
            ]
            db.add_all(projects)
            db.commit()

        # 4. Seed initial automation tasks
        if not db.query(AutomationTask).first():
            print("Seeding: Creating initial automation tasks")
            tasks = [
                AutomationTask(
                    title="Implement Redis Caching Layer",
                    priority="HIGH PRIORITY",
                    tags=["BACKEND", "PERFORMANCE"],
                    assignee_name="Alex Rivera",
                    assignee_role="Senior Infrastructure Engineer",
                    assignee_avatar="AR",
                    reason="Matches expertise in **distributed systems** and previously optimized the Auth microservice cache. High availability during this sprint cycle.",
                    border_color="border-blue-600",
                    full_width=False,
                    status="PENDING"
                ),
                AutomationTask(
                    title="Refactor Hook Patterns",
                    priority="STANDARD",
                    tags=["FRONTEND", "REFACTOR"],
                    assignee_name="Sarah Chen",
                    assignee_role="Frontend Lead",
                    assignee_avatar="SC",
                    reason="Directly matches expertise in React hooks and functional components. Has context on the original implementation flaws.",
                    border_color="border-blue-300",
                    full_width=False,
                    status="PENDING"
                ),
                AutomationTask(
                    title="Database Schema Migration",
                    priority="CRITICAL",
                    tags=["DATABASE", "MIGRATION"],
                    assignee_name="Marcus Aurelius",
                    assignee_role="DBA Consultant",
                    assignee_avatar="MA",
                    reason="Critical changes. Marcus has 98% success rate in PostgreSQL migrations.",
                    border_color="border-blue-600",
                    full_width=True,
                    status="PENDING"
                )
            ]
            db.add_all(tasks)
            db.commit()

        # 5. Seed admin user
        admin_email = "admin@trackiq.ai"
        admin_user = db.query(User).filter(User.email == admin_email).first()
        if not admin_user:
            print(f"Seeding: Creating admin user {admin_email}")
            admin_user = User(
                email=admin_email,
                full_name="TrackIQ Administrator",
                hashed_password=hash_password("admin123"),
                is_super_admin=True,
                is_verified=True
            )
            db.add(admin_user)
            db.commit()
        elif not admin_user.is_super_admin:
            print(f"Update: Promoting {admin_email} to Super Admin")
            admin_user.is_super_admin = True
            db.commit()

        # 6. Seed Project Board
        if not db.query(Board).first():
            print("Seeding: Creating initial Kanban Board")
            first_project = db.query(Project).first()
            project_id = first_project.id if first_project else None
            
            board = Board(name="Banc.ly frontend", description="Next-gen software project", project_id=project_id)
            db.add(board)
            db.commit()
            db.refresh(board)
            
            # Create default columns
            columns = [
                BoardColumn(board_id=board.id, name="TO DO", order=0),
                BoardColumn(board_id=board.id, name="IN PROGRESS", order=1),
                BoardColumn(board_id=board.id, name="QA", order=2),
                BoardColumn(board_id=board.id, name="DONE", order=3)
            ]
            db.add_all(columns)
            
            # Create default epics
            epics = [
                BoardEpic(board_id=board.id, name="ENDEAVOUR", color="bg-indigo-100 text-indigo-700"),
                BoardEpic(board_id=board.id, name="EXPERIENCE", color="bg-purple-100 text-purple-700")
            ]
            db.add_all(epics)
            db.commit()
            
            # Create sample tasks
            to_do_col = next(c for c in columns if c.name == "TO DO")
            in_prog_col = next(c for c in columns if c.name == "IN PROGRESS")
            qa_col = next(c for c in columns if c.name == "QA")
            
            sample_tasks = [
                BoardTask(
                    column_id=to_do_col.id, 
                    title="Implement Redis Caching Layer", 
                    identifier="BE-101", 
                    priority="High",
                    assignee_name="Alex Rivera",
                    assignee_avatar="AR"
                ),
                BoardTask(
                    column_id=in_prog_col.id, 
                    title="Refactor Hook Patterns", 
                    identifier="FE-402", 
                    priority="Medium",
                    assignee_name="Sarah Chen",
                    assignee_avatar="SC"
                ),
                BoardTask(
                    column_id=qa_col.id, 
                    title="Database Schema Migration", 
                    identifier="DB-88", 
                    priority="Critical",
                    assignee_name="Marcus Aurelius",
                    assignee_avatar="MA"
                )
            ]
            db.add_all(sample_tasks)
            db.commit()

    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()
