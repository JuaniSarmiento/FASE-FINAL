from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.incident import Incident

class IncidentRepository(ABC):
    @abstractmethod
    def save(self, incident: Incident) -> None:
        pass

    @abstractmethod
    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        pass

    @abstractmethod
    def list_by_student(self, student_id: str) -> List[Incident]:
        pass

    @abstractmethod
    def list_all(self) -> List[Incident]:
        pass
