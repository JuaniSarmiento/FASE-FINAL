import sys
import os
import uuid

# Add 'Fase Final' to path 
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from sqlalchemy.orm import Session
from src.infrastructure.persistence.database import SessionLocal
from src.infrastructure.persistence.models.learning_models import ActivityModel
from src.infrastructure.persistence.models.ai_tutor_models import TutorSessionModel

def test_connection():
    print("🔌 Testing DB Read/Write...")
    db: Session = SessionLocal()
    try:
        # 1. Write Activity
        activity_id = str(uuid.uuid4())
        new_activity = ActivityModel(
            id=activity_id,
            course_id="TEST-101",
            title="Smoke Test Activity",
            type="practice",
            description="Created by test_db_connection.py"
        )
        db.add(new_activity)
        
        # 2. Write Tutor Session
        session_id = str(uuid.uuid4())
        new_session = TutorSessionModel(
            id=session_id,
            student_id="TEST-USER-001"
        )
        db.add(new_session)
        
        db.commit()
        print("✅ Inserted Test Data.")
        
        # 3. Read Back
        saved_activity = db.query(ActivityModel).filter_by(id=activity_id).first()
        saved_session = db.query(TutorSessionModel).filter_by(id=session_id).first()
        
        if saved_activity and saved_session:
            print(f"✅ Read Verification: Found Activity '{saved_activity.title}' and Session '{saved_session.id}'")
        else:
            print("❌ Read Verification FAILED.")
            
        # Cleanup
        db.delete(saved_activity)
        db.delete(saved_session)
        db.commit()
        print("✅ Cleanup complete.")
        
    except Exception as e:
        print(f"❌ DB Test Failed: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    test_connection()
