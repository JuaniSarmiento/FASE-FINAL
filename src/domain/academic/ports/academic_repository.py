from abc import ABC, abstractmethod
from typing import List, Optional
from ..entities.subject import Subject
from ..entities.course import Course
from ..entities.enrollment import Enrollment

class SubjectRepository(ABC):
    @abstractmethod
    def save(self, subject: Subject) -> None:
        pass

    @abstractmethod
    def find_by_id(self, subject_id: str) -> Optional[Subject]:
        pass

    @abstractmethod
    def list_all(self) -> List[Subject]:
        pass

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
    def list_all(self) -> List[Course]:
        pass

class EnrollmentRepository(ABC):
    @abstractmethod
    def save(self, enrollment: Enrollment) -> None:
        pass

    @abstractmethod
    def find_by_student_and_course(self, student_id: str, course_id: str) -> Optional[Enrollment]:
        pass

    @abstractmethod
    def list_by_student(self, student_id: str) -> List[Enrollment]:
        pass
