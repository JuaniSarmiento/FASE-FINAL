from abc import ABC, abstractmethod
from typing import List, Dict, Any

class IAiAuditor(ABC):
    @abstractmethod
    def audit_activity(self, exercises: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Audit a list of exercises and return feedback and grade.
        exercises: List of dicts with keys: title, difficulty, code, passed.
        Returns: Dict with keys: final_grade, general_feedback, exercises_audit.
        """
        pass
