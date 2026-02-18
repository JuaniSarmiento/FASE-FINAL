from ....domain.learning.ports.activity_repository import ActivityRepository
from ...shared.unit_of_work import UnitOfWork
from ....domain.learning.entities.activity import Activity, ActivityType
from ....domain.learning.value_objects.exercise_status import ExerciseStatus
from ..dtos.activity_dtos import CreateActivityRequest, ActivityResponse
import uuid

class CreateActivityCommand:
    def __init__(self, activity_repository: ActivityRepository, unit_of_work: UnitOfWork):
        self.activity_repository = activity_repository
        self.unit_of_work = unit_of_work

    def execute(self, request: CreateActivityRequest, teacher_id: str) -> ActivityResponse:
        activity_id = str(uuid.uuid4())
        activity = Activity.create(
            id=activity_id,
            course_id=request.course_id,
            teacher_id=teacher_id,
            title=request.title,
            description=request.description or "",
            type=ActivityType(request.type)
        )
        
        with self.unit_of_work:
            self.activity_repository.save(activity)
            # Commit is handled by __exit__ if no exception, 
            # or we can call explicitly if we want to catch errors here.
            # But relying on __exit__ is standard for this UoW implementation.
        
        
        return ActivityResponse(
            id=activity.id,
            course_id=activity.course_id,
            teacher_id=activity.teacher_id,
            title=activity.title,
            description=activity.description,
            type=activity.type.value,
            status=activity.status.value,
            order=activity.order,
            created_at=activity.created_at,
            updated_at=activity.updated_at
        )
