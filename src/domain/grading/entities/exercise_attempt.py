from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.domain.shared.entity import Entity
from ..value_objects.execution_result import ExecutionResult

@dataclass(kw_only=True)
class ExerciseAttempt(Entity):
    exercise_id: str
    code_submitted: str
    result: Optional[ExecutionResult] = None
    time_taken_seconds: Optional[int] = None
    passed: bool = False
    grade: Optional[float] = None
    created_at: datetime = field(default_factory=datetime.now)
