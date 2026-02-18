import sys
import os
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.learning.commands.publish_activity_command import PublishActivityCommand
from src.domain.learning.value_objects.exercise_status import ExerciseStatus

def test_publish():
    print("--- Testing PublishActivityCommand Manually ---")
    db = next(get_db())
    repo = SqlAlchemyActivityRepository(db)
    uow = SqlAlchemyUnitOfWork(lambda: db)
    command = PublishActivityCommand(repo, uow)
    
    activity_id = "21144773-92ac-4d2a-844a-7a1496199200" # The drafted activity in Modulo 2
    
    print(f"Fetching activity {activity_id}...")
    activity = repo.find_by_id(activity_id)
    if not activity:
        print("Activity not found!")
        return

    print(f"Current Status: {activity.status}")
    print(f"Current Course ID: {activity.course_id}")
    
    print("Executing Publish Command...")
    # validating if the module id is needed. It is already linked effectively, but let's pass it if we want to be sure.
    # The output said it is linked to '22b57c9f-f048-4778-bde2-ce7f08dc6210' (Modulo 2).
    # Let's try without passing course_id first, to see if publish works isolated.
    try:
        command.execute(activity_id)
        print("Command Executed.")
    except Exception as e:
        print(f"Command Failed: {e}")
        return

    # User re-fetch to verify
    db.expire_all() # Ensure we fetch from DB
    
    updated_activity = repo.find_by_id(activity_id)
    print(f"New Status: {updated_activity.status}")
    
    if updated_activity.status == ExerciseStatus.PUBLISHED:
        print("SUCCESS: Activity is now PUBLISHED.")
    else:
        print("FAILURE: Activity is still DRAFT.")

if __name__ == "__main__":
    test_publish()
