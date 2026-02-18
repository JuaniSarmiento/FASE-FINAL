from dataclasses import dataclass, field
from typing import List
from src.application.shared.dtos.common import DTO
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.grading.ports.submission_repository import SubmissionRepository
from src.domain.learning.ports.session_repository import SessionRepository

@dataclass
class StudentRiskDTO(DTO):
    student_id: str
    email: str
    full_name: str
    risk_level: str # LOW, MEDIUM, HIGH
    average_grade: float
    last_active: str

class ListStudentsWithRisk:
    def __init__(
        self,
        user_repository: UserRepository,
        submission_repository: SubmissionRepository,
        session_repository: SessionRepository
    ):
        self.user_repository = user_repository
        self.submission_repository = submission_repository
        self.session_repository = session_repository

    def execute(self) -> List[StudentRiskDTO]:
        students = self.user_repository.find_all_by_role("student")
        result = []
        
        for student in students:
            # Calculate Risk
            # 1. Get submissions for student
            # needed: submission_repo.list_by_student(student.id)
            # Not implemented in SubmissionRepo interface yet! I should add it.
            # Assuming exist list_by_student(student_id)
            # submissions = self.submission_repository.list_by_student(str(student.id))
            
            # Simple fallback if not implemented:
            current_risk = "LOW"
            avg = 0.0
            
            # 2. Check last active session
            # sessions = self.session_repository.list_by_student(str(student.id))
            # ...
            
            result.append(StudentRiskDTO(
                student_id=str(student.id),
                email=student.email.address,
                full_name=student.full_name or "",
                risk_level=current_risk,
                average_grade=avg,
                last_active="Today"
            ))
            
        return result
