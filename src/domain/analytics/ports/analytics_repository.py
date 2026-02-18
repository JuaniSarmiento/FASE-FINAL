from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.risk_analysis import RiskAnalysis

class AnalyticsRepository(ABC):
    @abstractmethod
    def save(self, analysis: RiskAnalysis) -> None:
        pass

    @abstractmethod
    def find_latest_by_student(self, student_id: str) -> Optional[RiskAnalysis]:
        pass

    @abstractmethod
    def list_by_student(self, student_id: str) -> List[RiskAnalysis]:
        pass
