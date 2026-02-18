from abc import ABC, abstractmethod
from typing import Optional
from ..entities.tutor_session import TutorSession

class TutorSessionRepository(ABC):
    @abstractmethod
    def save(self, session: TutorSession) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, session_id: str) -> Optional[TutorSession]:
        pass
