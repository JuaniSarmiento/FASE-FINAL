from dataclasses import dataclass
from typing import List, Optional
from src.application.shared.dtos.common import DTO
from src.domain.learning.ports.activity_repository import ActivityRepository

@dataclass
class ActivitySummaryDTO(DTO):
    activity_id: str
    title: str
    description: str
    difficulty: str
    status: str

class ListStudentActivities:
    def __init__(self, activity_repository: ActivityRepository):
        self.activity_repository = activity_repository

    def execute(self, student_id: str) -> List[ActivitySummaryDTO]:
        # Logic: Get published activities visible to student
        # For MVP, maybe just return all published activities?
        activities = self.activity_repository.find_all_published()
        return [
            ActivitySummaryDTO(
                activity_id=a.id,
                title=a.title,
                description=a.description,
                difficulty="intermediate", # Default for activity summary
                status=a.status.value
            )
            for a in activities
        ]
