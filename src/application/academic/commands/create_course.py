from typing import Optional
from src.domain.academic.entities.course import Course
from src.domain.academic.ports.academic_repository import CourseRepository, SubjectRepository
from src.application.shared.unit_of_work import UnitOfWork
from src.application.academic.dtos.academic_dtos import CreateCourseRequest, CourseDTO

class CreateCourse:
    def __init__(self, 
                 course_repository: CourseRepository, 
                 subject_repository: SubjectRepository,
                 uow: UnitOfWork):
        self.course_repository = course_repository
        self.subject_repository = subject_repository
        self.uow = uow

    def execute(self, request: CreateCourseRequest) -> CourseDTO:
        # Validate Subject exists
        subject = self.subject_repository.find_by_id(request.subject_id)
        if not subject:
            raise ValueError(f"Subject with ID {request.subject_id} not found")

        course = Course.create(
            subject_id=request.subject_id,
            year=request.year,
            semester=request.semester
        )
        
        with self.uow:
            self.course_repository.save(course)
            
        return CourseDTO(
            id=course.id,
            subject_id=course.subject_id,
            year=course.year,
            semester=course.semester
        )
