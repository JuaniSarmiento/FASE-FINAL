from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.submission import Submission

class SubmissionRepository(ABC):
    @abstractmethod
    def save(self, submission: Submission) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, submission_id: str) -> Optional[Submission]:
        pass
        
    @abstractmethod
    def find_by_activity_and_student(self, activity_id: str, student_id: str) -> Optional[Submission]:
        pass

    @abstractmethod
    def list_by_student(self, student_id: str) -> List[Submission]:
        pass
