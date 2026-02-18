from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.academic.ports.academic_repository import SubjectRepository, CourseRepository, EnrollmentRepository
from src.domain.academic.entities.subject import Subject
from src.domain.academic.entities.course import Course
from src.domain.academic.entities.enrollment import Enrollment
from src.infrastructure.persistence.models.academic_models import SubjectModel, CourseModel, EnrollmentModel

class SqlAlchemySubjectRepository(SubjectRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, subject: Subject) -> None:
        model = self.db.query(SubjectModel).filter(SubjectModel.id == subject.id).first()
        if not model:
            model = SubjectModel(
                id=subject.id,
                name=subject.name,
                code=subject.code,
                description=subject.description
            )
            self.db.add(model)
        else:
            model.name = subject.name
            model.code = subject.code
            model.description = subject.description

    def find_by_id(self, subject_id: str) -> Optional[Subject]:
        model = self.db.query(SubjectModel).filter(SubjectModel.id == subject_id).first()
        if not model:
            return None
        return Subject(id=model.id, name=model.name, code=model.code, description=model.description)

    def list_all(self) -> List[Subject]:
        models = self.db.query(SubjectModel).all()
        return [Subject(id=m.id, name=m.name, code=m.code, description=m.description) for m in models]

class SqlAlchemyCourseRepository(CourseRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, course: Course) -> None:
        model = self.db.query(CourseModel).filter(CourseModel.id == course.id).first()
        if not model:
            model = CourseModel(
                id=course.id,
                subject_id=course.subject_id,
                year=course.year,
                semester=course.semester,
                active=course.active
            )
            self.db.add(model)
        else:
            model.subject_id = course.subject_id
            model.year = course.year
            model.semester = course.semester
            model.active = course.active

    def find_by_id(self, course_id: str) -> Optional[Course]:
        model = self.db.query(CourseModel).filter(CourseModel.id == course_id).first()
        if not model:
            return None
        return Course(id=model.id, subject_id=model.subject_id, year=model.year, semester=model.semester, active=model.active)

    def list_by_subject(self, subject_id: str) -> List[Course]:
        models = self.db.query(CourseModel).filter(CourseModel.subject_id == subject_id).all()
        return [Course(id=m.id, subject_id=m.subject_id, year=m.year, semester=m.semester, active=m.active) for m in models]

    def list_all(self) -> List[Course]:
        models = self.db.query(CourseModel).all()
        return [Course(id=m.id, subject_id=m.subject_id, year=m.year, semester=m.semester, active=m.active) for m in models]

class SqlAlchemyEnrollmentRepository(EnrollmentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, enrollment: Enrollment) -> None:
        model = self.db.query(EnrollmentModel).filter(EnrollmentModel.id == enrollment.id).first()
        if not model:
            model = EnrollmentModel(
                id=enrollment.id,
                student_id=enrollment.student_id,
                course_id=enrollment.course_id,
                status=enrollment.status,
                enrolled_at=enrollment.enrolled_at
            )
            self.db.add(model)
        else:
            model.status = enrollment.status

    def find_by_student_and_course(self, student_id: str, course_id: str) -> Optional[Enrollment]:
        model = self.db.query(EnrollmentModel).filter(
            EnrollmentModel.student_id == student_id,
            EnrollmentModel.course_id == course_id
        ).first()
        if not model:
            return None
        return Enrollment(
            id=model.id, 
            student_id=model.student_id, 
            course_id=model.course_id, 
            status=model.status, 
            enrolled_at=model.enrolled_at
        )

    def list_by_student(self, student_id: str) -> List[Enrollment]:
        models = self.db.query(EnrollmentModel).filter(EnrollmentModel.student_id == student_id).all()
        return [
            Enrollment(
                id=m.id, 
                student_id=m.student_id, 
                course_id=m.course_id, 
                status=m.status, 
                enrolled_at=m.enrolled_at
            ) for m in models
        ]
