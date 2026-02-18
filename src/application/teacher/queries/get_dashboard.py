from dataclasses import dataclass
from src.application.shared.dtos.common import DTO
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.learning.ports.activity_repository import ActivityRepository
# from src.domain.grading.ports.submission_repository import SubmissionRepository # If needed for stats

@dataclass
class TeacherDashboardDTO(DTO):
    total_students: int
    total_activities: int
    active_students: int # Placeholder

class GetTeacherDashboard:
    def __init__(
        self,
        user_repository: UserRepository,
        activity_repository: ActivityRepository
    ):
        self.user_repository = user_repository
        self.activity_repository = activity_repository

    def execute(self) -> TeacherDashboardDTO:
        # Simple counts
        # specific methods in repo needed? or list_all and len()? Use list_all for MVP.
        # UserRepo needs find_all_by_role("student")
        students = self.user_repository.find_all_by_role("student")
        
        # ActivityRepo needs find_all()
        # I implemented find_all_published, but teacher sees all?
        # Maybe list_by_course("default")?
        # Let's assume list_by_course(default_course) for now.
        activities = self.activity_repository.list_by_course("101") # Default course ID
        
        return TeacherDashboardDTO(
            total_students=len(students),
            total_activities=len(activities),
            active_students=len([s for s in students if s.is_active])
        )
