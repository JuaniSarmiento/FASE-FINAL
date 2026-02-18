import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

from textwrap import dedent
from sqlalchemy import text
from src.infrastructure.persistence.database import get_db
from src.application.student.queries.list_courses import ListStudentCourses
import uuid

from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository

def debug():
    print("--- Debugging Module Enrollment ---")
    
    # Get Sync Session
    db_gen = get_db()
    session = next(db_gen)
    
    try:
        # 1. Setup Data
        student_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO users (id, username, email, hashed_password, roles, is_active, created_at, updated_at)
            VALUES (:id, :username, :email, :pwd, :roles, true, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET id = users.id RETURNING id
        """), {
            "id": student_id,
            "username": f"debug_student_{student_id[:8]}",
            "email": f"debug_student_{student_id[:8]}@test.com",
            "pwd": "hashed_password",
            "roles": '{student}'
        })
        print(f"1. Student created: {student_id}")
        
        # Create "Module" (Activity of type module)
        module_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activities (id, title, course_id, teacher_id, type, status, created_at, updated_at)
            VALUES (:id, 'Debug Module', 'default_course', 'mock_teacher', 'module', 'published', NOW(), NOW())
        """), {"id": module_id})
        print(f"2. Module created: {module_id}")

        # Create "Tutorial" Activity inside the Module
        reading_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activities (id, title, course_id, teacher_id, type, status, created_at, updated_at)
            VALUES (:id, 'Debug Tutorial', :mid, 'mock_teacher', 'tutorial', 'published', NOW(), NOW())
        """), {"id": reading_id, "mid": module_id})
        print(f"2a. Activity created inside module: {reading_id}")

        # Assign Student to Module
        assignment_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activity_assignments (id, activity_id, student_id, assigned_at)
            VALUES (:id, :mid, :uid, NOW())
        """), {"id": assignment_id, "mid": module_id, "uid": student_id})
        session.commit()
        print(f"3. Student assigned to Module: {assignment_id}")
        
        # 4. Verify Database State
        result = session.execute(text("""
            SELECT * FROM activity_assignments WHERE student_id = :uid AND activity_id = :mid
        """), {"uid": student_id, "mid": module_id}).fetchone()
        
        if result:
            print("   [DB Check] Assignment record found in database.")
        # 5. Execute ListStudentCourses Query
        print("4. Executing ListStudentCourses query...")
        repo = SqlAlchemyActivityRepository(session)
        query = ListStudentCourses(repo)
        courses = query.execute(student_id)
        
        found = False
        print(f"   [Query Result] Found {len(courses)} courses.")
        for c in courses:
            print(f"   - Course: {c.name} (modules: {len(c.modules)})")
            for m in c.modules:
                # print(f"     * Module: {m.module_id} - {m.title}")
                if m.module_id == module_id:
                    print(f"     ✅ Found target module: {m.title}")
                    print(f"     📂 Activities in module: {len(m.activities)}")
                    for act in m.activities:
                        print(f"       - {act.title} [{act.status}]")
                    found = True
        
        if not found:
            print("   ❌ Target module NOT found in ListStudentCourses result.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    debug()
