from dataclasses import dataclass
from src.domain.shared.entity import Entity

@dataclass(kw_only=True)
class Course(Entity):
    subject_id: str
    year: int
    semester: int
    active: bool = True

    @classmethod
    def create(cls, subject_id: str, year: int, semester: int) -> 'Course':
        return cls(subject_id=subject_id, year=year, semester=semester)
