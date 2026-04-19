from sqlalchemy import inspect, text
from app.core.database import engine, Base, SessionLocal
from app.models.user import User
from app.models.admin import SystemSettings, AuditLog, OrganizationProfile
from app.models.project import Project
from app.models.automation import AutomationTask
from app.core.security import hash_password

def init_db():
    # 1. Create all missing tables
    Base.metadata.create_all(bind=engine)
    
    # 2. Check for missing columns in existing tables (Self-healing)
    inspector = inspect(engine)
    
    # Check 'users' table for 'is_super_admin'
    columns = [c['name'] for c in inspector.get_columns("users")]
    if "is_super_admin" not in columns:
        print("Migrating: Adding 'is_super_admin' column to 'users' table")
        with engine.connect() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN is_super_admin BOOLEAN DEFAULT FALSE"))
            conn.commit()

    db = SessionLocal()
    try:
        # 3. Seed initial projects
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
    except Exception as e:
        print(f"Error during seeding: {e}")
        db.rollback()
    finally:
        db.close()
