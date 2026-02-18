from typing import Optional
from src.domain.academic.entities.enrollment import Enrollment
from src.domain.academic.ports.academic_repository import EnrollmentRepository, CourseRepository
from src.domain.identity.ports.user_repository import UserRepository
from src.domain.identity.value_objects.user_id import UserId
from src.application.shared.unit_of_work import UnitOfWork
from src.application.academic.dtos.academic_dtos import EnrollStudentRequest, EnrollmentDTO

class EnrollStudent:
    def __init__(self, 
                 enrollment_repository: EnrollmentRepository,
                 course_repository: CourseRepository,
                 user_repository: UserRepository,
                 uow: UnitOfWork):
        self.enrollment_repository = enrollment_repository
        self.course_repository = course_repository
        self.user_repository = user_repository
        self.uow = uow

    def execute(self, request: EnrollStudentRequest) -> EnrollmentDTO:
        # Validate Course
        course = self.course_repository.find_by_id(request.course_id)
        if not course:
            raise ValueError(f"Course {request.course_id} not found")
            
        # Validate Student
        student = self.user_repository.find_by_id(UserId(request.student_id))
        if not student:
            raise ValueError(f"Student {request.student_id} not found")
            
        # Check existing enrollment ?
        existing = self.enrollment_repository.find_by_student_and_course(request.student_id, request.course_id)
        if existing:
            raise ValueError("Student already enrolled")

        enrollment = Enrollment.create(
            student_id=request.student_id,
            course_id=request.course_id
        )
        
        with self.uow:
            self.enrollment_repository.save(enrollment)
            
        return EnrollmentDTO(
            id=enrollment.id,
            student_id=enrollment.student_id,
            course_id=enrollment.course_id,
            status=enrollment.status
        )
