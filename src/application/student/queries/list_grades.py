from dataclasses import dataclass
from typing import List, Optional
from src.application.shared.dtos.common import DTO
from sqlalchemy.orm import Session
from src.infrastructure.persistence.models.grading_models import SubmissionModel
from src.infrastructure.persistence.models.learning_models import ActivityModel

@dataclass
class GradeDTO(DTO):
    grade_id: str
    activity_id: str
    grade: float
    activity_title: str
    passed: bool
    course_name: Optional[str] = None
    max_grade: int = 100
    teacher_feedback: Optional[str] = None

class ListStudentGrades:
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def execute(self, student_id: str) -> List[GradeDTO]:
        # Join Submission and Activity
        results = (
            self.db_session.query(SubmissionModel, ActivityModel)
            .join(ActivityModel, SubmissionModel.activity_id == ActivityModel.id)
            .filter(SubmissionModel.student_id == student_id)
            .filter(SubmissionModel.final_score.isnot(None)) # Only graded ones
            .all()
        )
        
        grades = []
        for sub, act in results:
            grades.append(GradeDTO(
                grade_id=sub.id,
                activity_id=act.id,
                grade=sub.final_score if sub.final_score is not None else 0.0,
                activity_title=act.title,
                passed=(sub.final_score if sub.final_score is not None else 0.0) >= 60, # Business rule assumption
                course_name=act.course_id, # Or join with Course if needed
                max_grade=100,
                teacher_feedback="Evaluación completada" # Placeholder or fetch from somewhere
            ))
            
        return grades
