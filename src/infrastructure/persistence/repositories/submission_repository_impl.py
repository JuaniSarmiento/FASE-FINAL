from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.grading.ports.submission_repository import SubmissionRepository
from src.domain.grading.entities.submission import Submission
from src.domain.grading.value_objects.submission_status import SubmissionStatus
from src.domain.grading.value_objects.score import Score
from src.infrastructure.persistence.models.grading_models import SubmissionModel, ExerciseAttemptModel

class SqlAlchemySubmissionRepository(SubmissionRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save(self, submission: Submission) -> None:
        model = self.db_session.query(SubmissionModel).filter(SubmissionModel.id == str(submission.id)).first() # id is usually uuid in entity base
        # Wait, Entity.id is string? Or UUID object? 
        # Base entity usually has self.id as string (if using my generic Entity).
        # Need to check Entity implementation if it uses ValueObject for ID.
        # Assuming string for simplicity of this implementation plan.
        
        sid = str(submission.id)
        if not model:
            model = SubmissionModel(
                id=sid,
                student_id=submission.student_id,
                activity_id=submission.activity_id,
                status=submission.status.value,
                final_score=submission.score.value if submission.score else None,
                created_at=submission.created_at,
                updated_at=submission.updated_at
            )
            self.db_session.add(model)
        else:
            model.status = submission.status.value
            model.final_score = submission.score.value if submission.score else None
            model.updated_at = submission.updated_at

        # Save Attempts
        for attempt in submission.attempts:
             att_model = self.db_session.query(ExerciseAttemptModel).filter(ExerciseAttemptModel.id == str(attempt.id)).first()
             if not att_model:
                 att_model = ExerciseAttemptModel(
                     id=str(attempt.id),
                     submission_id=sid,
                     exercise_id=attempt.exercise_id,
                     code_submitted=attempt.code_submitted,
                     is_passing=attempt.passed,
                     grade=attempt.grade,
                     execution_output=attempt.result.stdout if attempt.result else "",
                     error_message=attempt.result.error if attempt.result else "",
                     created_at=attempt.created_at
                 )
                 self.db_session.add(att_model)
             else:
                 # Update existing attempt
                 att_model.code_submitted = attempt.code_submitted
                 att_model.is_passing = attempt.passed
                 att_model.grade = attempt.grade
                 att_model.execution_output = attempt.result.stdout if attempt.result else att_model.execution_output
                 att_model.error_message = attempt.result.error if attempt.result else att_model.error_message

    def find_by_activity_and_student(self, activity_id: str, student_id: str) -> Optional[Submission]:
        model = self.db_session.query(SubmissionModel).filter(
            SubmissionModel.activity_id == activity_id,
            SubmissionModel.student_id == student_id
        ).first()
        if not model:
            return None
        
        return self._to_entity(model)

    def find_by_id(self, submission_id: str) -> Optional[Submission]:
        model = self.db_session.query(SubmissionModel).filter(SubmissionModel.id == submission_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def list_by_student(self, student_id: str) -> List[Submission]:
        models = self.db_session.query(SubmissionModel).filter(SubmissionModel.student_id == student_id).all()
        return [self._to_entity(m) for m in models]

    def _to_entity(self, model: SubmissionModel) -> Submission:
        sub = Submission(
            activity_id=model.activity_id,
            student_id=model.student_id
        )
        sub.id = model.id # Force ID
        sub.status = SubmissionStatus(model.status)
        if model.final_score is not None:
            sub.score = Score(model.final_score)
        
        sub.created_at = model.created_at
        sub.updated_at = model.updated_at
        
        # Load attempts (lazy loading issues?)
        # Ideally we eagerly load or accessing model.attempts triggers it within session.
        # But here we convert to entity.
        # We need to map attempts too if we want them in entity.
        # For MVP, let's skip deep mapping unless used. 
        # SubmitSolution uses `add_attempt`, so it maintains in memory list.
        # Finding submission should probably load them.
        return sub
