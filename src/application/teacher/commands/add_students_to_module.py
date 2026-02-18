from dataclasses import dataclass
from typing import List
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.application.shared.unit_of_work import UnitOfWork

@dataclass
class AddStudentsToModuleCommand:
    activity_repository: ActivityRepository
    unit_of_work: UnitOfWork

    def execute(self, module_id: str, student_ids: List[str]) -> None:
        with self.unit_of_work:
            for student_id in student_ids:
                self.activity_repository.add_student_to_module(module_id, student_id)
            self.unit_of_work.commit()
