from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.commission import Commission

class CommissionRepository(ABC):
    @abstractmethod
    def save(self, commission: Commission) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, commission_id: str) -> Optional[Commission]:
        pass
        
    @abstractmethod
    def list_by_course(self, course_id: str) -> List[Commission]:
        pass
