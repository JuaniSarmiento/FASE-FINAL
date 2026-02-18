import sys
import os
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models.learning_models import SessionModel, ExerciseModel, ActivityModel
from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel
from sqlalchemy import text

def debug_session(session_id: str):
    print(f"--- Debugging Session: {session_id} ---")
    db = next(get_db())
    
    # 1. Get Session
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        print(f"❌ Session {session_id} NOT FOUND.")
        # Try to list recent sessions
        print("Recent sessions:")
        recent = db.query(SessionModel).order_by(SessionModel.created_at.desc()).limit(5).all()
        for s in recent:
            print(f" - {s.id} (Activity: {s.activity_id})")
        return

    print(f"✅ Session Found. Activity ID: {session.activity_id}")
    
    # 2. Get Activity
    activity = db.query(ActivityModel).filter(ActivityModel.id == session.activity_id).first()
    if activity:
        print(f"✅ Activity Found: {activity.title} (Type: {activity.type})")
        print(f"   Description: {activity.description}")
    else:
        print("❌ Activity NOT FOUND.")

    # 3. List Exercises
    exercises = db.query(ExerciseModel).filter(ExerciseModel.activity_id == session.activity_id).all()
    print(f"Found {len(exercises)} exercises for this activity.")
    for i, ex in enumerate(exercises):
        print(f" [Ex {i+1}] ID: {ex.id}")
        print(f"        Title: {ex.title}")
        print(f"        Difficulty: '{ex.difficulty}' (Type: {type(ex.difficulty)})")
        print(f"        Language: '{ex.language}' (Type: {type(ex.language)})")
        print(f"        Status: '{ex.status}' (Type: {type(ex.status)})")
        print(f"        TestCases JSON: {repr(ex.test_cases_json)}")
        try:
            import json
            if ex.test_cases_json:
                json.loads(ex.test_cases_json)
                print("        [OK] JSON parses successfully")
            else:
                print("        [OK] Empty/None JSON")
        except Exception as e:
            print(f"        [ERROR] JSON Parse Error: {e}")

    # 4. Check TutorMessageModel columns and table existence
    print("\n--- Checking TutorMessageModel ---")
    from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel
    print(f"Role column: {TutorMessageModel.role.type}")
    
    try:
        count = db.query(TutorMessageModel).count()
        print(f"Table 'tutor_messages' exists. Row count: {count}")
    except Exception as e:
        print(f"Error querying tutor_messages: {e}")
    
if __name__ == "__main__":
    # session_id from user logs
    target_session = "52b4a350-4f2b-4568-a93e-a1aada44528c"  # New session ID from recent logs
    debug_session(target_session)
