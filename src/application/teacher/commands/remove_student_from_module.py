from dataclasses import dataclass
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.application.shared.unit_of_work import UnitOfWork

@dataclass
class RemoveStudentFromModuleCommand:
    activity_repository: ActivityRepository
    unit_of_work: UnitOfWork

    def execute(self, module_id: str, student_id: str) -> None:
        with self.unit_of_work:
            self.activity_repository.remove_student_from_module(module_id, student_id)
            self.unit_of_work.commit()
