from dataclasses import dataclass, field
from datetime import datetime
from src.domain.shared.entity import Entity

@dataclass(kw_only=True)
class Enrollment(Entity):
    student_id: str
    course_id: str
    status: str = "active" # active, completed, dropped
    enrolled_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, student_id: str, course_id: str) -> 'Enrollment':
        return cls(student_id=student_id, course_id=course_id)
