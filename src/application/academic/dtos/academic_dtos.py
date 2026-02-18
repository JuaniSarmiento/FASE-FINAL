from dataclasses import dataclass
from src.application.shared.dtos.common import DTO

@dataclass
class CreateSubjectRequest(DTO):
    name: str
    code: str
    description: str = ""

@dataclass
class CreateCourseRequest(DTO):
    subject_id: str
    year: int
    semester: int

@dataclass
class EnrollStudentRequest(DTO):
    student_id: str
    course_id: str

@dataclass
class SubjectDTO(DTO):
    id: str
    name: str
    code: str

@dataclass
class CourseDTO(DTO):
    id: str
    subject_id: str
    year: int
    semester: int
    active: bool = True

@dataclass
class EnrollmentDTO(DTO):
    id: str
    student_id: str
    course_id: str
    status: str
