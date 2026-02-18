import sys
import os
import time

# Add 'Fase Final' to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from sqlalchemy.exc import OperationalError
from src.infrastructure.config.settings import settings
from src.infrastructure.persistence.database import engine, Base

# Import ALL models so Base.metadata knows them
from src.infrastructure.persistence.models import learning_models
from src.infrastructure.persistence.models import grading_models
from src.infrastructure.persistence.models import ai_tutor_models
# Add other models here if created

def wait_for_db():
    print("⏳ Waiting for database connection...")
    retries = 5
    while retries > 0:
        try:
            conn = engine.connect()
            conn.close()
            print("✅ Database connected!")
            return True
        except OperationalError:
            print(f"⚠️ Database not ready. Retries left: {retries}")
            time.sleep(2)
            retries -= 1
    return False

def init_db():
    if not wait_for_db():
        print("❌ Could not connect to database. Exiting.")
        sys.exit(1)
        
    print("🛠️ Creating tables...")
    try:
        # Create all tables defined in models
        Base.metadata.create_all(bind=engine)
        print("✅ Tables created successfully!")
        
        # Verify specific tables exist (loose check)
        from sqlalchemy import inspect
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Existing tables: {tables}")
        
        required_tables = ["activities", "exercises", "submissions", "exercise_attempts", "tutor_sessions", "cognitive_traces"]
        missing = [t for t in required_tables if t not in tables]
        
        if missing:
            print(f"⚠️ WARNING: Missing tables: {missing}")
        else:
            print("✨ All critical Phase 4 tables present.")
            
    except Exception as e:
        print(f"❌ Error creating tables: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
