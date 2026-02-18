from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List
from src.domain.shared.entity import AggregateRoot
from ..value_objects.exercise_status import ExerciseStatus

class ActivityType(str, Enum):
    PRACTICE = "practice"
    EXAM = "exam"
    TUTORIAL = "tutorial"
    MODULE = "module"
    CODING = "coding"
    READING = "reading"

@dataclass(kw_only=True)
class Activity(AggregateRoot):
    course_id: str
    teacher_id: str
    title: str
    description: str
    type: ActivityType
    status: ExerciseStatus = ExerciseStatus.DRAFT
    order: int = 0
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def publish(self) -> None:
        self.status = ExerciseStatus.PUBLISHED
        self.updated_at = datetime.now()

    @classmethod
    def create(cls, id: str, course_id: str, teacher_id: str, title: str, 
               description: str, type: ActivityType) -> 'Activity':
        """
        Factory method to create an Activity with enforcing domain rules.
        Rule: Modules are always created as PUBLISHED. Other activities as DRAFT.
        """
        # Business Rule: Modules are auto-published
        initial_status = ExerciseStatus.PUBLISHED if type == ActivityType.MODULE else ExerciseStatus.DRAFT
        
        return cls(
            id=id,
            course_id=course_id,
            teacher_id=teacher_id,
            title=title,
            description=description,
            type=type,
            status=initial_status
        )
