from abc import ABC, abstractmethod
from typing import List
from src.domain.learning.entities.exercise import Exercise
from src.domain.learning.value_objects.difficulty import Difficulty
from src.domain.learning.value_objects.programming_language import ProgrammingLanguage

class IExerciseGenerator(ABC):
    """
    Interface for the AI Service that generates exercises.
    Application Layer doesn't know it's Mistral or Ollama.
    """
    
    @abstractmethod
    def generate(
        self, 
        topic: str, 
        count: int, 
        difficulty: Difficulty, 
        language: ProgrammingLanguage,
        context: str = None
    ) -> List[Exercise]:
        pass
