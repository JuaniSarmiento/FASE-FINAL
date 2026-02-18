import sys
import os
import uuid
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.submission_repository_impl import SqlAlchemySubmissionRepository
from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.student.queries.list_grades import ListStudentGrades
from src.domain.learning.entities.activity import Activity, ActivityType
from src.domain.grading.entities.submission import Submission
from src.domain.grading.value_objects.score import Score
from src.domain.learning.value_objects.exercise_status import ExerciseStatus

def test_list_grades():
    print("--- Testing List Student Grades ---")
    db = next(get_db())
    sub_repo = SqlAlchemySubmissionRepository(db)
    act_repo = SqlAlchemyActivityRepository(db)
    uow = SqlAlchemyUnitOfWork(lambda: db)
    
    student_id = "student_grades_test"
    
    # 1. Create a graded submission
    # Need Activity first
    activity_id = "act_grade_" + str(uuid.uuid4())[:8]
    activity = Activity(
        id=activity_id,
        course_id="c1",
        teacher_id="t1",
        title="Graded Activity",
        description="...",
        type=ActivityType.PRACTICE,
        status=ExerciseStatus.PUBLISHED
    )
    with uow:
        act_repo.save(activity)
        uow.commit()

    # Create Submission
    submission = Submission(activity_id=activity_id, student_id=student_id)
    submission.grade(Score(85.0))
    
    with uow:
        sub_repo.save(submission)
        uow.commit()
        
    print(f"Created submission for student {student_id} with grade 85.0")
    
    # 2. Query
    query = ListStudentGrades(db)
    grades = query.execute(student_id)
    
    print(f"Found {len(grades)} grades for student {student_id}")
    for g in grades:
        print(f" - {g.activity_title}: {g.grade} (Passed: {g.passed})")
        
    if len(grades) > 0 and grades[0].grade == 85.0:
        print("SUCCESS: Grade retrieved correctly.")
    else:
        print("FAILURE: Grade not found or incorrect.")

if __name__ == "__main__":
    test_list_grades()
