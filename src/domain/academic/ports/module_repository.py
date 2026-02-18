from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.module import Module

class ModuleRepository(ABC):
    @abstractmethod
    def save(self, module: Module) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, module_id: str) -> Optional[Module]:
        pass
        
    @abstractmethod
    def list_by_course(self, course_id: str) -> List[Module]:
        pass
