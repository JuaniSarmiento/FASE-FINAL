from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.enrollment import Enrollment

class EnrollmentRepository(ABC):
    @abstractmethod
    def save(self, enrollment: Enrollment) -> None:
        pass
        
    @abstractmethod
    def find_by_id(self, enrollment_id: str) -> Optional[Enrollment]:
        pass
        
    @abstractmethod
    def find_by_student_and_course(self, student_id: str, commission_id: str) -> Optional[Enrollment]:
        pass
        
    @abstractmethod
    def list_by_student(self, student_id: str) -> List[Enrollment]:
        pass
