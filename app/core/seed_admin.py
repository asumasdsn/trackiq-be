from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.admin import SystemSettings, OrganizationProfile, PermissionModule
from app.models.marketing import ProductFeature

def seed_admin_data():
    db = SessionLocal()
    try:
        # 1. Seed System Settings (Global Config)
        settings_defaults = [
            {"key": "system_timezone", "value": "UTC-08:00 Pacific Time", "description": "Default regional temporal node"},
            {"key": "api_retry_limit", "value": "5", "description": "Failure tolerance for external handshakes"},
            {"key": "worker_timeout", "value": "30000", "description": "Latency threshold for background nodes"},
            {"key": "data_retention", "value": "90", "description": "Archival window for telemetry logs"},
        ]
        for s in settings_defaults:
            if not db.query(SystemSettings).filter_by(key=s["key"]).first():
                db.add(SystemSettings(**s))

        # 2. Seed Organization Profile
        if not db.query(OrganizationProfile).first():
            db.add(OrganizationProfile(
                name="Anbu4 TrackIQ Enterprise",
                industry="Deep Tech / Automation",
                address="Neural Grid Node 7, Silicon Valley",
                primary_contact_name="Anbu4 Administrator",
                primary_contact_email="admin@trackiq.enterprise"
            ))

        # 3. Seed Permission Modules
        modules = [
            {"name": "Automation Nodes", "description": "logical sensor inputs and branching", "icon_name": "Zap", "category": "Operation", "default_permissions": [1, 1, 1, 0, 1]},
            {"name": "Asset Library", "description": "Components and script templates", "icon_name": "FileText", "category": "Operation", "default_permissions": [1, 1, 1, 1, 1]},
            {"name": "Predictive Analytics", "description": "Real-time metrics and ML forecasting", "icon_name": "Activity", "category": "Systems", "default_permissions": [1, 0, 0, 0, 1]},
            {"name": "Billing & Usage", "description": "Invoicing and usage quotas", "icon_name": "Shield", "category": "Finance", "default_permissions": [0, 0, 0, 0, 0]},
        ]
        for m in modules:
            if not db.query(PermissionModule).filter_by(name=m["name"]).first():
                db.add(PermissionModule(**m))

        # 4. Seed Product Features (Onboarding Guide)
        product_features = [
            {
                "title": "Neural Project Matrix",
                "description": "Orchestrate complex engineering workflows through intuitive, high-density Kanban nodes and live team telemetry.",
                "icon_name": "Layout",
                "benefit_highlight": "35% faster cycle times",
                "category": "Platform",
                "display_order": 1
            },
            {
                "title": "GenAI Automation Core",
                "description": "Deploy advanced Llama-3 synthesis to autonomously generate project plans, tasks, and resource allocations in seconds.",
                "icon_name": "Zap",
                "benefit_highlight": "Zero manual tasking",
                "category": "AI",
                "display_order": 2
            },
            {
                "title": "High-Density Issues Hub",
                "description": "Identify and neutralize platform risks with chromatic chromatic priority weighting and real-time blocker tracking.",
                "icon_name": "AlertTriangle",
                "benefit_highlight": "Risk-zero delivery",
                "category": "Analytics",
                "display_order": 3
            },
            {
                "title": "Admin Intelligence Gate",
                "description": "Gain absolute visibility into AI operational costs, token consumption, and neural trigger frequency through the Admin Hub.",
                "icon_name": "Brain",
                "benefit_highlight": "Total cost observability",
                "category": "Admin",
                "display_order": 4
            }
        ]
        for f in product_features:
            if not db.query(ProductFeature).filter_by(title=f["title"]).first():
                db.add(ProductFeature(**f))

        db.commit()
    except Exception as e:
        print(f"Seed synchronization failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_admin_data()
    print("Admin Intelligence Matrix Seeded Successfully.")
