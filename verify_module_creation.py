import sys
import os
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.application.learning.commands.create_activity_command import CreateActivityCommand
from src.application.learning.dtos.activity_dtos import CreateActivityRequest
from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

def verify_creation():
    print("--- Verifying Module Creation Status ---")
    
    db_gen = get_db()
    session = next(db_gen)
    
    try:
        repo = SqlAlchemyActivityRepository(session)
        # Mock UoW that just uses the session
        class MockUoW:
            def __enter__(self): return self
            def __exit__(self, exc_type, exc_val, exc_tb): 
                if not exc_type: session.commit()
                
        uow = MockUoW()
        
        command = CreateActivityCommand(repo, uow)
        
        # Test 1: Create Module
        print("1. Creating Module...")
        req_module = CreateActivityRequest(
            title="Auto Published Module",
            course_id="default_course",
            type="module"
        )
        module_res = command.execute(req_module, "teacher_123")
        print(f"   Module Status: {module_res.status}")
        
        if module_res.status == "published":
            print("   ✅ PASS: Module is published.")
        else:
            print("   ❌ FAIL: Module is NOT published.")

        # Test 2: Create Coding Activity
        print("2. Creating Coding Activity...")
        req_coding = CreateActivityRequest(
            title="Draft Coding Activity",
            course_id="default_course",
            type="practice"
        )
        coding_res = command.execute(req_coding, "teacher_123")
        print(f"   Activity Status: {coding_res.status}")
        
        if coding_res.status == "draft":
            print("   ✅ PASS: Coding Activity is draft.")
        else:
            print("   ❌ FAIL: Coding Activity is NOT draft.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

if __name__ == "__main__":
    verify_creation()
