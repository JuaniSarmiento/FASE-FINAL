from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.activity import Activity

class ActivityRepository(ABC):
    @abstractmethod
    def save(self, activity: Activity) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, activity_id: str) -> Optional[Activity]:
        pass
        
    @abstractmethod
    def list_by_course(self, course_id: str) -> List[Activity]:
        pass

    @abstractmethod
    def list_by_teacher(self, teacher_id: str) -> List[Activity]:
        pass

    @abstractmethod
    def find_all_published(self) -> List[Activity]:
        pass

    @abstractmethod
    def add_student_to_module(self, module_id: str, student_id: str) -> None:
        pass

    @abstractmethod
    def remove_student_from_module(self, module_id: str, student_id: str) -> None:
        pass

    @abstractmethod
    def get_assigned_students(self, module_id: str) -> List[str]:
        pass


