from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.infrastructure.persistence.database import get_db
from src.infrastructure.http.dependencies.container import get_unit_of_work, get_user_repository
from src.infrastructure.persistence.repositories.academic_repository_impl import (
    SqlAlchemySubjectRepository, SqlAlchemyCourseRepository, SqlAlchemyEnrollmentRepository
)
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.application.academic.commands.create_subject import CreateSubject
from src.application.academic.commands.create_course import CreateCourse
from src.application.academic.commands.enroll_student import EnrollStudent
from typing import List
from src.application.academic.dtos.academic_dtos import (
    CreateSubjectRequest, CreateCourseRequest, EnrollStudentRequest, SubjectDTO, CourseDTO, EnrollmentDTO
)

router = APIRouter()

# Dependencies
def get_subject_repository(db: Session = Depends(get_db)):
    return SqlAlchemySubjectRepository(db)

def get_course_repository(db: Session = Depends(get_db)):
    return SqlAlchemyCourseRepository(db)

def get_enrollment_repository(db: Session = Depends(get_db)):
    return SqlAlchemyEnrollmentRepository(db)

@router.post("/subjects", response_model=SubjectDTO)
def create_subject(
    request: CreateSubjectRequest,
    repo: SqlAlchemySubjectRepository = Depends(get_subject_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)
):
    command = CreateSubject(repo, uow)
    return command.execute(request)

@router.post("/courses", response_model=CourseDTO)
def create_course(
    request: CreateCourseRequest,
    repo: SqlAlchemyCourseRepository = Depends(get_course_repository),
    subject_repo: SqlAlchemySubjectRepository = Depends(get_subject_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)
):
    command = CreateCourse(repo, subject_repo, uow)
    return command.execute(request)

@router.get("/courses", response_model=List[CourseDTO])
def list_courses(
    repo: SqlAlchemyCourseRepository = Depends(get_course_repository)
):
    courses = repo.list_all()
    return [
        CourseDTO(
            id=c.id,
            subject_id=c.subject_id,
            year=c.year,
            semester=c.semester,
            active=c.active
        ) for c in courses
    ]

@router.post("/enrollments", response_model=EnrollmentDTO)
def enroll_student(
    request: EnrollStudentRequest,
    repo: SqlAlchemyEnrollmentRepository = Depends(get_enrollment_repository),
    course_repo: SqlAlchemyCourseRepository = Depends(get_course_repository),
    user_repo = Depends(get_user_repository),
    uow: SqlAlchemyUnitOfWork = Depends(get_unit_of_work)
):
    try:
        command = EnrollStudent(repo, course_repo, user_repo, uow)
        return command.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
