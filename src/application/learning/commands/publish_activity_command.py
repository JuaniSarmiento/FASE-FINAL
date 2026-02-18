from src.application.shared.unit_of_work import UnitOfWork
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.learning.exceptions import ActivityNotFoundException

class PublishActivityCommand:
    def __init__(self, activity_repository: ActivityRepository, unit_of_work: UnitOfWork):
        self.activity_repository = activity_repository
        self.unit_of_work = unit_of_work

    def execute(self, activity_id: str, course_id: str = None) -> None:
        activity = self.activity_repository.find_by_id(activity_id)
        if not activity:
            raise ActivityNotFoundException(f"Activity {activity_id} not found")
        
        print(f"DEBUG: Publishing activity {activity_id}. Current status: {activity.status}")
        activity.publish()
        print(f"DEBUG: New status: {activity.status}")
        
        if course_id:
            print(f"DEBUG: Updating course_id to {course_id}")
            activity.course_id = course_id
        
        with self.unit_of_work:
            print("DEBUG: Saving activity...")
            self.activity_repository.save(activity)
            self.unit_of_work.commit()
            print("DEBUG: Commit successful.")
