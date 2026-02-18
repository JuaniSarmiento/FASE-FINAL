from dataclasses import dataclass
from typing import List
from src.application.shared.dtos.common import DTO
from src.domain.learning.value_objects.difficulty import Difficulty
from src.domain.learning.value_objects.programming_language import ProgrammingLanguage

@dataclass
class GenerateExercisesRequest(DTO):
    activity_id: str
    topic: str
    count: int = 1
    difficulty: str = "Medium" # String to be converted to Enum in UseCase
    language: str = "python" # String to be converted to Enum in UseCase

@dataclass
class GeneratedExerciseDTO(DTO):
    id: str
    title: str
    problem_statement: str
    difficulty: str
    language: str
