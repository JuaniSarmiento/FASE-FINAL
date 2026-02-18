from dataclasses import dataclass
from src.application.shared.unit_of_work import UnitOfWork
from src.application.shared.dtos.common import DTO
from src.domain.learning.ports.session_repository import SessionRepository
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.learning.entities.session import LearningSession
from src.domain.learning.value_objects.session_status import SessionStatus

@dataclass
class StartSessionRequest(DTO):
    student_id: str
    activity_id: str
    mode: str = "standard"

class StartLearningSession:
    def __init__(
        self,
        session_repository: SessionRepository,
        activity_repository: ActivityRepository,
        unit_of_work: UnitOfWork
    ):
        self.session_repository = session_repository
        self.activity_repository = activity_repository
        self.unit_of_work = unit_of_work

    def execute(self, request: StartSessionRequest) -> LearningSession:
        # Check if activity exists
        activity = self.activity_repository.find_by_id(request.activity_id)
        if not activity:
            raise ValueError("Activity not found")

        # Create Session
        session = LearningSession(
            student_id=request.student_id,
            activity_id=request.activity_id,
            status=SessionStatus.ACTIVE
            # Add mode if supported by entity
        )

        with self.unit_of_work:
            self.session_repository.save(session)
            self.unit_of_work.commit()

        return session
