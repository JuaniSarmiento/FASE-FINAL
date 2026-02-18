from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.course import Course
from ..value_objects.academic_period import AcademicPeriod

class CourseRepository(ABC):
    @abstractmethod
    def save(self, course: Course) -> None:
        pass
    
    @abstractmethod
    def find_by_id(self, course_id: str) -> Optional[Course]:
        pass
        
    @abstractmethod
    def list_by_subject(self, subject_id: str) -> List[Course]:
        pass
        
    @abstractmethod
    def list_active(self) -> List[Course]:
        pass
