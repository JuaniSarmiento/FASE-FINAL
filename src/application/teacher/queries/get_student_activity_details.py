from typing import Optional
from src.domain.grading.ports.submission_read_repository import SubmissionReadRepository, StudentActivityDetailsDTO

class GetStudentActivityDetails:
    def __init__(self, repository: SubmissionReadRepository):
        self.repository = repository

    def execute(self, activity_id: str, student_id: str) -> Optional[StudentActivityDetailsDTO]:
        return self.repository.get_student_activity_details(activity_id, student_id)
