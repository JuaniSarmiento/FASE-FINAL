from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.domain.shared.entity import AggregateRoot
from ..value_objects.schedule import Schedule
from ..value_objects.access_code import AccessCode

@dataclass
class Commission(AggregateRoot):
    course_id: str
    name: str  # e.g., "A", "Morning Group"
    teacher_id: Optional[str] = None
    schedule: Optional[Schedule] = None
    access_code: Optional[AccessCode] = None
    max_students: int = 50
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def assign_teacher(self, teacher_id: str) -> None:
        self.teacher_id = teacher_id
        self.updated_at = datetime.now()
        
    def set_schedule(self, schedule: Schedule) -> None:
        self.schedule = schedule
        self.updated_at = datetime.now()
        
    def generate_access_code(self) -> None:
        self.access_code = AccessCode.generate()
        self.updated_at = datetime.now()
