import sys
import os
import uuid
import time
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.submission_repository_impl import SqlAlchemySubmissionRepository
from src.infrastructure.persistence.repositories.exercise_repository_impl import SqlAlchemyExerciseRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.grading.local_code_executor import LocalCodeExecutor
from src.infrastructure.ai.llm.ollama_auditor import OllamaAuditor
from src.application.student.commands.submit_solution import SubmitSolution, SubmitSolutionRequest

def test_grading():
    print("--- Testing Grading Logic ---")
    db = next(get_db())
    sub_repo = SqlAlchemySubmissionRepository(db)
    ex_repo = SqlAlchemyExerciseRepository(db)
    executor = LocalCodeExecutor()
    auditor = OllamaAuditor()
    uow = SqlAlchemyUnitOfWork(lambda: db)
    
    command = SubmitSolution(sub_repo, ex_repo, executor, auditor, uow)
    
    # Needs valid activity and student?
    # For grading, it fetches exercises by ID. I need queryable exercises.
    # If I don't have real exercises in DB, `find_by_id` fails.
    # The Auditor needs `title` and `difficulty` from exercise.
    
    # Mocking exercise repo find_by_id?
    # Or inserting a dummy exercise first.
    
    print("Pre-requisite: Need an exercise in DB.")
    # I'll rely on the fact that if exercise is missing, command skips it but still calls auditor with what it found?
    # The command:
    # for ex_id, code in request.all_exercise_codes.items():
    #     ex = self.exercise_repository.find_by_id(ex_id)
    #     if ex: ...
    
    # So if no exercises found, nothing to audit.
    # I should insert a dummy exercise.
    
    from src.domain.learning.entities.exercise import Exercise, TestCase
    from src.domain.learning.value_objects.difficulty import Difficulty
    from src.domain.learning.value_objects.programming_language import ProgrammingLanguage
    from src.domain.learning.value_objects.exercise_status import ExerciseStatus
    
    from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
    from src.domain.learning.entities.activity import Activity, ActivityType
    
    act_repo = SqlAlchemyActivityRepository(db)
    
    # Create Activity
    activity_id = "test_activity_grading_" + str(uuid.uuid4())[:8]
    activity = Activity(
        id=activity_id,
        course_id="test_course",
        teacher_id="test_teacher",
        title="Activity for Grading Test",
        description="Testing grading",
        type=ActivityType.PRACTICE,
        status=ExerciseStatus.PUBLISHED
    )
    
    with uow:
        act_repo.save(activity)
        uow.commit()
    print(f"Created dummy activity {activity_id}")

    ex_id = str(uuid.uuid4())
    exercise = Exercise(
        id=ex_id,
        activity_id=activity_id,
        title="Sumar dos números",
        problem_statement="Suma a y b",
        starter_code="a = 1\nb=2",
        difficulty=Difficulty.EASY,
        language=ProgrammingLanguage.PYTHON,
        status=ExerciseStatus.PUBLISHED,
        test_cases=[]
    )
    
    with uow:
        ex_repo.save(exercise)
        uow.commit()
    print(f"Created dummy exercise {ex_id}")
    
    # Now submit
    req = SubmitSolutionRequest(
        session_id="test_session_grading",
        student_id="test_student_grading",
        activity_id=activity_id,
        is_final_submission=True,
        all_exercise_codes={
            ex_id: "print(1+2)"
        }
    )
    
    print("Executing SubmitSolution with audit...")
    try:
        res = command.execute(req)
        print(f"Result Grade: {res.grade}")
        print(f"Feedback: {res.feedback}")
        print(f"Details: {res.details}")
        if res.grade > 0 or "Error" in res.feedback:
             print("SUCCESS: Grading attempt made (even if error or 0).")
        else:
             print("WARNING: Grade is 0, check logic.")
             
    except Exception as e:
        print(f"ERROR: {e}")

if __name__ == "__main__":
    test_grading()
