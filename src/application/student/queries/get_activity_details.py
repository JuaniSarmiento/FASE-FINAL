from dataclasses import dataclass
from typing import List, Optional
from src.application.shared.dtos.common import DTO
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.learning.ports.exercise_repository import ExerciseRepository

@dataclass
class ExerciseDTO(DTO):
    exercise_id: str
    title: str
    problem_statement: str
    starter_code: str
    difficulty: str
    language: str
    order: int = 0
    # Add status if needed

@dataclass
class ActivityDetailsDTO(DTO):
    activity_id: str
    title: str
    description: str
    type: str
    status: str
    exercises: List[ExerciseDTO]
    course_id: str

class GetActivityDetails:
    def __init__(
        self, 
        activity_repository: ActivityRepository,
        exercise_repository: ExerciseRepository
    ):
        self.activity_repository = activity_repository
        self.exercise_repository = exercise_repository

    def execute(self, activity_id: str) -> Optional[ActivityDetailsDTO]:
        activity = self.activity_repository.find_by_id(activity_id)
        if not activity:
            return None
            
        exercises = self.exercise_repository.list_by_activity(activity_id)
        
        # Sort exercises by title (Entity does not have order field yet)
        exercises.sort(key=lambda x: x.title)
        
        exercise_dtos = [
            ExerciseDTO(
                exercise_id=ex.id,
                title=ex.title,
                problem_statement=ex.problem_statement,
                starter_code=ex.starter_code,
                difficulty=ex.difficulty.value,
                language=ex.language.value,
                order=0 # Default, or fetch from somewhere else if needed
            )
            for ex in exercises
        ]
        
        return ActivityDetailsDTO(
            activity_id=activity.id,
            title=activity.title,
            description=activity.description or "",
            type=activity.type.value,
            status=activity.status.value,
            exercises=exercise_dtos,
            course_id=activity.course_id
        )
