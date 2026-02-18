from dataclasses import dataclass, field
from typing import Optional, Dict, List, Any
from src.application.shared.dtos.common import DTO
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.learning.ports.exercise_repository import ExerciseRepository
from src.domain.grading.ports.submission_repository import SubmissionRepository
from src.domain.grading.ports.code_executor import CodeExecutor
from src.domain.grading.ports.ai_auditor import IAiAuditor
from src.domain.grading.entities.submission import Submission
from src.domain.grading.entities.exercise_attempt import ExerciseAttempt
from src.domain.grading.value_objects.score import Score
from src.domain.grading.value_objects.execution_result import ExecutionResult

@dataclass
class SubmitSolutionRequest(DTO):
    session_id: str
    student_id: str
    activity_id: str
    exercise_id: Optional[str] = None
    code: str = ""
    language: str = "python"
    is_final_submission: bool = False
    all_exercise_codes: Optional[Dict[str, str]] = None

@dataclass
class SubmitSolutionResponse(DTO):
    grade: int
    feedback: str
    passed: bool
    execution: Optional[Dict[str, Any]] = None
    details: Dict[str, Any] = field(default_factory=dict)

class SubmitSolution:
    def __init__(
        self,
        submission_repository: SubmissionRepository,
        exercise_repository: ExerciseRepository,
        code_executor: CodeExecutor,
        ai_auditor: IAiAuditor,
        unit_of_work: UnitOfWork
    ):
        self.submission_repository = submission_repository
        self.exercise_repository = exercise_repository
        self.code_executor = code_executor
        self.ai_auditor = ai_auditor
        self.unit_of_work = unit_of_work

    def execute(self, request: SubmitSolutionRequest) -> SubmitSolutionResponse:
        # 1. Execute Code (if single exercise)
        exec_res: Optional[ExecutionResult] = None
        passed = False
        execution_dict = None
        
        if request.exercise_id and request.code:
             exercise = self.exercise_repository.find_by_id(request.exercise_id)
             if exercise:
                 exec_res = self.code_executor.execute(
                     code=request.code,
                     language=request.language,
                     test_cases=exercise.test_cases
                 )
                 passed = exec_res.is_success
                 execution_dict = {
                     "stdout": exec_res.stdout,
                     "stderr": exec_res.stderr,
                     "error": exec_res.error,
                     "success": exec_res.is_success
                 }
        
        # 2. Handle Final Submission (Audit)
        final_grade = 0
        final_feedback = ""
        audit_details = {}

        if request.is_final_submission and request.all_exercise_codes:
            exercises_to_audit = []
            for ex_id, code in request.all_exercise_codes.items():
                ex = self.exercise_repository.find_by_id(ex_id)
                if ex:
                    exercises_to_audit.append({
                        "id": ex.id,
                        "title": ex.title,
                        "difficulty": ex.difficulty.value,
                        "code": code,
                        "passed": True # Assumption
                    })
            
            audit_result = self.ai_auditor.audit_activity(exercises_to_audit)
            final_grade = int(audit_result.get("final_grade", 0))
            final_feedback = audit_result.get("general_feedback", "")
            # Ensure details contains the full audit structure for frontend
            audit_details = audit_result

        # 3. Save Submission
        with self.unit_of_work:
             submission = self.submission_repository.find_by_activity_and_student(
                 request.activity_id, request.student_id
             )
             if not submission:
                 submission = Submission(
                     activity_id=request.activity_id,
                     student_id=request.student_id
                 )
             
             # Record individual attempt (Manual Run)
             if request.exercise_id and exec_res:
                 attempt = ExerciseAttempt(
                     exercise_id=request.exercise_id,
                     code_submitted=request.code,
                     result=exec_res,
                     passed=passed
                 )
                 submission.add_attempt(attempt)

             # Implement Final Submission Attempts from Audit
             if request.is_final_submission and audit_details:
                 for ex_audit in audit_details.get("exercises_audit", []):
                     # Try to find exercise_id from audit or request
                     ex_id = ex_audit.get("exercise_id")
                     
                     # If Ollama didn't return ID (fallback), try to match by order if request.all_exercise_codes is ordered?
                     # Since we added ID to prompt, we hope it's there. 
                     # If not, we skip or log? 
                     # For MVP, assuming ID is present as we added it to prompt.
                     
                     if ex_id:
                         # Create execution result from feedback
                         audit_exec_res = ExecutionResult(
                             stdout=ex_audit.get("feedback", ""),
                             stderr="",
                             error="",
                             exit_code=0 if ex_audit.get("passed", False) else 1
                         )
                         
                         code_for_ex = request.all_exercise_codes.get(ex_id, "") if request.all_exercise_codes else ""
                         
                         graded_attempt = ExerciseAttempt(
                             exercise_id=ex_id,
                             code_submitted=code_for_ex,
                             result=audit_exec_res,
                             passed=ex_audit.get("passed", False),
                             grade=float(ex_audit.get("grade", 0))
                         )
                         submission.add_attempt(graded_attempt)

             # Update final grade if audited
             if request.is_final_submission:
                 submission.grade(Score(float(final_grade)))
             
             self.submission_repository.save(submission)
             self.unit_of_work.commit()
             
             # TRIGGER ASYNC RISK ANALYSIS
             if request.is_final_submission:
                 try:
                     from src.infrastructure.tasks.analyze_risk_task import enqueue_risk_analysis
                     # Accessing raw ID might strictly violate Clean Arch if not exposed, but Entity usually exposes ID.
                     # submission.id should be available.
                     enqueue_risk_analysis(
                         submission_id=submission.id,
                         student_id=request.student_id,
                         activity_id=request.activity_id
                     )
                 except Exception as e:
                     print(f"Error triggering risk analysis: {e}")

        return SubmitSolutionResponse(
            grade=final_grade,
            feedback=final_feedback or "Code executed.",
            passed=passed if not request.is_final_submission else final_grade >= 60,
            execution=execution_dict,
            details=audit_details
        )
