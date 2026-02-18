import sys
import os
import uuid
from datetime import datetime
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel
from src.infrastructure.persistence.models.learning_models import SessionModel

def debug_chat_insert():
    session_id = "52b4a350-4f2b-4568-a93e-a1aada44528c"
    print(f"--- Debugging Chat Insert for Session: {session_id} ---")
    
    db = next(get_db())
    
    # 1. Verify Session Exists
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        print("❌ Session NOT FOUND. Cannot insert message.")
        return

    print("✅ Session Found.")

    # 2. Try Insert
    msg_id = str(uuid.uuid4())
    print(f"Attempting to insert TutorMessageModel with id={msg_id}")
    
    msg = TutorMessageModel(
        id=msg_id,
        session_id=session_id,
        role="student",
        content="Debug message content",
        created_at=datetime.utcnow()
    )
    
    try:
        db.add(msg)
        db.commit()
        print("✅ Insert SUCCESSFUL.")
    except Exception as e:
        print(f"❌ Insert FAILED: {e}")
        db.rollback()

if __name__ == "__main__":
    debug_chat_insert()
