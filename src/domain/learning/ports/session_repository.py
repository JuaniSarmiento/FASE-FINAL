from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.session import LearningSession

class SessionRepository(ABC):
    @abstractmethod
    def save(self, session: LearningSession) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[LearningSession]:
        pass
        
    @abstractmethod
    def list_by_student(self, student_id: str) -> List[LearningSession]:
        pass
        
    @abstractmethod
    def find_active_by_student(self, student_id: str) -> Optional[LearningSession]:
        pass
