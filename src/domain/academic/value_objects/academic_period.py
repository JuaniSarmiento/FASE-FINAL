from dataclasses import dataclass
from datetime import datetime
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class AcademicPeriod(ValueObject):
    year: int
    semester: int  # 1 or 2
    
    def __post_init__(self):
        if self.year < 2000 or self.year > 2100:
             raise ValueError("Invalid year")
        if self.semester not in [1, 2]:
            raise ValueError("Semester must be 1 or 2")
            
    def __str__(self) -> str:
        return f"{self.year}-{self.semester}"
        
    @staticmethod
    def current() -> 'AcademicPeriod':
        now = datetime.now()
        semester = 1 if now.month <= 7 else 2
        return AcademicPeriod(year=now.year, semester=semester)
