from src.application.shared.unit_of_work import UnitOfWork
from src.domain.learning.ports.exercise_repository import ExerciseRepository
from src.domain.grading.ports.submission_repository import SubmissionRepository
from src.domain.grading.ports.code_executor import CodeExecutor
from src.domain.grading.entities.submission import Submission
from src.domain.grading.entities.exercise_attempt import ExerciseAttempt
from src.domain.grading.value_objects.submission_status import SubmissionStatus
from src.domain.learning.exceptions import ExerciseInvalidException
from ..dtos.submit_exercise_dto import SubmitExerciseRequest, ExerciseSubmissionResultDTO

class SubmitExercise:
    def __init__(
        self,
        submission_repository: SubmissionRepository,
        exercise_repository: ExerciseRepository,
        code_executor: CodeExecutor,
        unit_of_work: UnitOfWork
    ):
        self.submission_repository = submission_repository
        self.exercise_repository = exercise_repository
        self.code_executor = code_executor
        self.unit_of_work = unit_of_work
        
    def execute(self, request: SubmitExerciseRequest) -> ExerciseSubmissionResultDTO:
        # 1. Fetch Exercise
        exercise = self.exercise_repository.find_by_id(request.exercise_id)
        if not exercise:
            raise ExerciseInvalidException(f"Exercise {request.exercise_id} not found")
            
        # 2. Execute Code in Sandbox (Port)
        execution_result = self.code_executor.execute(
            code=request.code_submitted,
            language=request.language,
            test_cases=exercise.test_cases
        )
        
        # 3. Find or Create Submission Aggregate
        submission = self.submission_repository.find_by_activity_and_student(
            request.activity_id, request.student_id
        )
        
        if not submission:
            submission = Submission(
                activity_id=request.activity_id,
                student_id=request.student_id
            )
            
        # 4. Create Attempt Entity
        attempt = ExerciseAttempt(
            exercise_id=exercise.id,
            code_submitted=request.code_submitted,
            result=execution_result,
            passed=execution_result.is_success
        )
        
        # 5. Add Attempt to Submission
        submission.add_attempt(attempt)
        
        # 6. Save State
        with self.unit_of_work:
            self.submission_repository.save(submission)
            self.unit_of_work.commit()
            
        return ExerciseSubmissionResultDTO(
            success=True,
            passed=execution_result.is_success,
            stdout=execution_result.stdout,
            stderr=execution_result.stderr,
            error=execution_result.error
        )
