from typing import List
from ....domain.learning.ports.activity_repository import ActivityRepository
from ..dtos.activity_dtos import ActivityResponse

class ListTeacherActivitiesQuery:
    def __init__(self, activity_repository: ActivityRepository):
        self.activity_repository = activity_repository

    def execute(self, teacher_id: str) -> List[ActivityResponse]:
        activities = self.activity_repository.list_by_teacher(teacher_id)
        return [
            ActivityResponse(
                id=a.id,
                course_id=a.course_id,
                teacher_id=a.teacher_id,
                title=a.title,
                description=a.description,
                type=a.type.value,
                status=a.status.value,
                order=a.order,
                created_at=a.created_at,
                updated_at=a.updated_at
            ) for a in activities
        ]
