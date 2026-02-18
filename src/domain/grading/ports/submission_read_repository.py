from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class StudentActivityDetailsDTO:
    student_id: str
    activity_id: str
    activity_title: str
    status: str
    final_grade: float
    submitted_at: str
    exercises: List[Dict[str, Any]]
    chat_history: List[Dict[str, str]]
    code_submitted: str
    risk_analysis: Optional[Dict[str, Any]] = None

class SubmissionReadRepository(ABC):
    @abstractmethod
    def get_student_activity_details(self, activity_id: str, student_id: str) -> Optional[StudentActivityDetailsDTO]:
        """
        Retrieves detailed activity information for a student, including submission status,
        grades, exercises, code, and chat history.
        """
        pass
