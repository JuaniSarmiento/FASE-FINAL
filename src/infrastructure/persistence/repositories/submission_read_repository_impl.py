from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from src.domain.grading.ports.submission_read_repository import SubmissionReadRepository, StudentActivityDetailsDTO
from src.infrastructure.persistence.models.grading_models import SubmissionModel, ExerciseAttemptModel
from src.infrastructure.persistence.models.learning_models import ActivityModel, SessionModel
from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel

class SqlAlchemySubmissionReadRepository(SubmissionReadRepository):
    def __init__(self, session: Session):
        self.session = session

    def get_student_activity_details(self, activity_id: str, student_id: str) -> Optional[StudentActivityDetailsDTO]:
        # 1. Fetch Submission
        submission = (
            self.session.query(SubmissionModel)
            .filter_by(activity_id=activity_id, student_id=student_id)
            .first()
        )

        # 2. Fetch Activity
        activity = self.session.query(ActivityModel).filter_by(id=activity_id).first()
        if not activity:
            return None

        # 3. Fetch Session & Chats
        session = (
            self.session.query(SessionModel)
            .filter_by(activity_id=activity_id, student_id=student_id)
            .order_by(SessionModel.updated_at.desc())
            .first()
        )
        
        chat_history = []
        if session:
            chats = (
                self.session.query(TutorMessageModel)
                .filter_by(session_id=session.id)
                .order_by(TutorMessageModel.created_at.asc())
                .all()
            )
            chat_history = [
                {"role": c.role, "content": c.content, "timestamp": c.created_at.isoformat()}
                for c in chats
            ]

        # 4. Construct Data
        grade = submission.final_score if submission and submission.final_score is not None else 0.0
        status = "submitted" if submission else "pending"
        
        exercises_details = []
        code_parts = []
        
        if submission:
            attempts = (
                self.session.query(ExerciseAttemptModel)
                .filter_by(submission_id=submission.id)
                .all()
            )
            for attempt in attempts:
                exercises_details.append({
                    "exercise_id": attempt.exercise_id,
                    "passed": attempt.is_passing,
                    "grade": attempt.grade if attempt.grade is not None else (100 if attempt.is_passing else 0),
                    "feedback": attempt.execution_output or attempt.error_message or "Sin feedback" 
                })
                if attempt.code_submitted:
                    code_parts.append(f"# Ejercicio {attempt.exercise_id}\n{attempt.code_submitted}\n")
                
        # Combine all code submissions
        full_code_submission = "\n".join(code_parts) if code_parts else "No se envió código"

        # Check for persisted risk analysis
        risk_analysis = None
        if submission and hasattr(submission, 'risk_analysis') and submission.risk_analysis:
            ra = submission.risk_analysis
            import json
            try:
                evidence = json.loads(ra.evidence) if ra.evidence else []
                positive_aspects = json.loads(ra.positive_aspects) if ra.positive_aspects else []
            except:
                evidence = []
                positive_aspects = []
                
            risk_analysis = {
                "risk_score": ra.risk_score,
                "risk_level": ra.risk_level,
                "diagnosis": ra.diagnosis,
                "evidence": evidence,
                "teacher_advice": ra.teacher_advice,
                "positive_aspects": positive_aspects,
                "analyzed_at": ra.analyzed_at.isoformat()
            }

        return StudentActivityDetailsDTO(
            student_id=student_id,
            activity_id=activity_id,
            activity_title=activity.title,
            status=status,
            final_grade=grade,
            submitted_at=submission.created_at.isoformat() if submission else "",
            exercises=exercises_details,
            chat_history=chat_history,
            code_submitted=full_code_submission,
            risk_analysis=risk_analysis
        )
