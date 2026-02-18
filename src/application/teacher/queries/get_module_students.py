from dataclasses import dataclass
from typing import List
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.identity.value_objects.user_id import UserId
from src.application.teacher.dtos.student_dto import StudentDTO

@dataclass
class GetModuleStudentsQuery:
    activity_repository: ActivityRepository
    user_repository: UserRepository

    def execute(self, module_id: str) -> List[StudentDTO]:
        student_ids = self.activity_repository.get_assigned_students(module_id)
        students = []
        for sid in student_ids:
            user = self.user_repository.find_by_id(UserId(sid))
            if user:
                students.append(StudentDTO(
                    user_id=user.id.value,
                    full_name=user.full_name or "Unknown",
                    email=user.email.address,
                    role="student",
                    status="active"
                ))
        return students
