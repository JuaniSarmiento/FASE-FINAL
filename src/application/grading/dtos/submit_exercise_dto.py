from dataclasses import dataclass
from typing import Optional
from src.application.shared.dtos.common import DTO

@dataclass
class SubmitExerciseRequest(DTO):
    student_id: str
    activity_id: str
    exercise_id: str
    code_submitted: str
    language: str

@dataclass
class ExerciseSubmissionResultDTO(DTO):
    success: bool
    passed: bool
    stdout: str
    stderr: str
    error: Optional[str] = None
