from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.domain.shared.entity import Entity
from ..value_objects.difficulty import Difficulty
from ..value_objects.programming_language import ProgrammingLanguage
from ..value_objects.exercise_status import ExerciseStatus
from .test_case import TestCase

@dataclass(kw_only=True)
class Exercise(Entity):
    activity_id: str
    title: str
    problem_statement: str
    starter_code: str
    difficulty: Difficulty
    language: ProgrammingLanguage
    status: ExerciseStatus = ExerciseStatus.DRAFT
    test_cases: List[TestCase] = field(default_factory=list)
    solution_code: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_test_case(self, test_case: TestCase) -> None:
        self.test_cases.append(test_case)
        self.updated_at = datetime.now()
        
    def publish(self) -> None:
        self.status = ExerciseStatus.PUBLISHED
        self.updated_at = datetime.now()
