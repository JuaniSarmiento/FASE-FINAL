from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.subject import Subject

class SubjectRepository(ABC):
    @abstractmethod
    def save(self, subject: Subject) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, subject_id: str) -> Optional[Subject]:
        pass
        
    @abstractmethod
    def list_all(self) -> List[Subject]:
        pass
