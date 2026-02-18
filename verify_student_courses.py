import sys
import os
# Add current directory to path
sys.path.append(os.getcwd())

from textwrap import dedent
from sqlalchemy import text
from src.infrastructure.persistence.database import get_db
from src.application.student.queries.list_courses import ListStudentCourses
import uuid

def verify():
    print("--- Verifying Student Courses ---")
    
    # Get Sync Session
    db_gen = get_db()
    session = next(db_gen)
    
    try:
        # 1. Setup Data
        # Create Student
        student_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO users (id, username, email, hashed_password, roles, is_active, created_at, updated_at)
            VALUES (:id, :username, :email, :pwd, :roles, true, NOW(), NOW())
            ON CONFLICT (email) DO UPDATE SET id = users.id RETURNING id
        """), {
            "id": student_id,
            "username": f"test_student_{student_id[:8]}",
            "email": f"student_{student_id[:8]}@test.com",
            "pwd": "hashed_password",
            "roles": '{student}'
        })
        print(f"Student created: {student_id}")
        
        # Create Subject & Course & Module
        subject_id = str(uuid.uuid4())
        course_id = str(uuid.uuid4())
        module_id = str(uuid.uuid4())
        
        # Create "Module" (Activity of type module)
        module_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activities (id, title, course_id, teacher_id, type, status, created_at, updated_at)
            VALUES (:id, 'Test Module Activity', 'default_course', 'mock_teacher', 'module', 'published', NOW(), NOW())
        """), {"id": module_id})
        
        # Create Sub-Activity (Exercise) linked to Module
        activity_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activities (id, title, course_id, teacher_id, type, status, created_at, updated_at)
            VALUES (:id, 'Child Activity', :mid, 'mock_teacher', 'coding', 'published', NOW(), NOW())
        """), {"id": activity_id, "mid": module_id})

        # Assign Student to Module
        assignment_id = str(uuid.uuid4())
        session.execute(text("""
            INSERT INTO activity_assignments (id, activity_id, student_id, assigned_at)
            VALUES (:id, :mid, :uid, NOW())
        """), {"id": assignment_id, "mid": module_id, "uid": student_id})
        
        session.commit()
        print("Setup complete: Student assigned to Module (Activity)")
        
        session.commit()
        print("Setup complete: Student enrolled in Course/Module")
        
        # 2. Execute Query
        query = ListStudentCourses(session)
        courses = query.execute(student_id)
        
        print(f"\n--- Results for student {student_id} ---")
        found = False
        for c in courses:
            print(f"Course: {c.name} ({c.year} {c.semester})")
            for m in c.modules:
                print(f"  - Module: {m.title} (Activities: {m.activity_count})")
            
            if c.course_id == 'default_course' and any(m.module_id == module_id for m in c.modules):
                found = True
        
        if found:
            print("\n✅ Verification SUCCESS: Course found!")
        else:
            print("\n❌ Verification FAILED: Course not found.")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        session.rollback()
    finally:
        session.close()

if __name__ == "__main__":
    verify()
