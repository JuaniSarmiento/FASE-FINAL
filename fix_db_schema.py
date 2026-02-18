import sys
import os
from sqlalchemy import text
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db, engine
from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel

def fix_schema():
    print("--- Fixing DB Schema ---")
    
    # 1. Drop tutor_messages
    print("Dropping table 'tutor_messages'...")
    with engine.connect() as conn:
        conn.execute(text("DROP TABLE IF EXISTS tutor_messages CASCADE"))
        conn.commit()
    print("Dropped.")

    # 2. Recreate it from Model
    print("Recreating 'tutor_messages' from SQLAlchmey Model...")
    TutorMessageModel.__table__.create(bind=engine)
    print("Recreated.")
    
    # 3. Verify FK
    from sqlalchemy import inspect
    inspector = inspect(engine)
    fks = inspector.get_foreign_keys("tutor_messages")
    print("\nNew FKs on 'tutor_messages':")
    for fk in fks:
        print(f" - {fk}")

    if any(fk['referred_table'] == 'sessions_v2' for fk in fks):
        print("\n✅ SUCCESS: FK now references 'sessions_v2'")
    else:
        print("\n❌ FAILURE: FK does not reference 'sessions_v2'")

if __name__ == "__main__":
    fix_schema()
