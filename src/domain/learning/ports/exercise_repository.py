from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.exercise import Exercise

class ExerciseRepository(ABC):
    @abstractmethod
    def save(self, exercise: Exercise) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, exercise_id: str) -> Optional[Exercise]:
        pass
        
    @abstractmethod
    def list_by_activity(self, activity_id: str) -> List[Exercise]:
        pass

    @abstractmethod
    def count_by_activity(self, activity_id: str) -> int:
        pass
