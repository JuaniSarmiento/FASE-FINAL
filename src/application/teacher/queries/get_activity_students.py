from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from src.infrastructure.persistence.models.learning_models import ActivityModel, SessionModel
from src.infrastructure.persistence.models.academic_models import EnrollmentModel
from src.infrastructure.persistence.models.user_models import UserModel
from src.infrastructure.persistence.models.grading_models import SubmissionModel

class StudentActivityProgressDTO(BaseModel):
    student_id: str
    email: str
    full_name: str
    total_exercises: int
    submitted_exercises: int
    avg_score: float
    progress_percentage: float
    status: str 

class GetActivityStudentsProgress:
    def __init__(self, db: Session):
        self.db = db

    def execute(self, activity_id: str) -> List[StudentActivityProgressDTO]:
        # ... (rest of the code is implicitly matched by context if I don't replace it all, but let's be safe and replace the class and execute method or just the DTO and the append part)
        
        # 1. Get Activity
        activity = self.db.query(ActivityModel).filter_by(id=activity_id).first()
        if not activity:
            return []

        # 2. Get Students Enrolled
        target_module_id = activity.course_id 
        if activity.type == 'module':
             target_module_id = activity.id
             
        enrollments = (
            self.db.query(EnrollmentModel)
            .filter_by(module_id=target_module_id)
            .all()
        )
        
        student_ids = [e.student_id for e in enrollments]
        if not student_ids:
            return []

        students = self.db.query(UserModel).filter(UserModel.id.in_(student_ids)).all()
        student_map = {s.id: s for s in students}
        
        # 3. Get Submissions
        submissions = (
            self.db.query(SubmissionModel)
            .filter(
                SubmissionModel.activity_id == activity_id,
                SubmissionModel.student_id.in_(student_ids)
            )
            .all()
        )
        
        submission_map = {s.student_id: s for s in submissions}
        
        # 4. Build Result
        results = []
        for student_id in student_ids:
            student = student_map.get(student_id)
            if not student: 
                continue
                
            submission = submission_map.get(student_id)
            
            # Default values
            submitted = 0
            avg = 0.0
            status = 'not_started'
            
            if submission:
                status = submission.status
                avg = submission.final_score if submission.final_score else 0.0
                
                if status in ['submitted', 'graded', 'pending', 'completed']:
                     submitted = 1 
                elif status == 'in_progress':
                     submitted = 0
            
            # Calculate progress
            total = 1 # TODO: Get real exercise count
            progress = (submitted / total) * 100 if total > 0 else 0.0

            results.append(StudentActivityProgressDTO(
                student_id=student.id,
                email=student.email or "",
                full_name=student.full_name or "Sin Nombre",
                total_exercises=total,
                submitted_exercises=submitted, 
                avg_score=avg,
                progress_percentage=progress,
                status=status
            ))
            
        return results
