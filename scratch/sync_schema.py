from sqlalchemy import text
from app.core.database import engine

def sync():
    print("Initiating Schema Synchronization...")
    try:
        with engine.connect() as conn:
            # Adding email column
            print("Adding 'email' column to 'employees' table...")
            conn.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS email VARCHAR;"))
            
            # Adding project_name column
            print("Adding 'project_name' column to 'employees' table...")
            conn.execute(text("ALTER TABLE employees ADD COLUMN IF NOT EXISTS project_name VARCHAR;"))
            
            conn.commit()
            print("✅ Schema elements synchronized successfully.")
    except Exception as e:
        print(f"❌ Synchronization failed: {e}")

if __name__ == "__main__":
    sync()
