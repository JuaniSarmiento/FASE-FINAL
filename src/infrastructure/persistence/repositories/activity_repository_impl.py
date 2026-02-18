from typing import Optional, List
from sqlalchemy.orm import Session
from ....domain.learning.ports.activity_repository import ActivityRepository
from ....domain.learning.entities.activity import Activity, ActivityType
from ....domain.learning.value_objects.exercise_status import ExerciseStatus
from ..models.learning_models import ActivityModel

class SqlAlchemyActivityRepository(ActivityRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, activity: Activity) -> None:
        model = self.session.query(ActivityModel).filter_by(id=activity.id).first()
        if not model:
            model = ActivityModel(id=activity.id)
            self.session.add(model)
        
        model.course_id = activity.course_id
        model.teacher_id = activity.teacher_id
        model.title = activity.title
        model.description = activity.description
        model.type = activity.type.value
        model.status = activity.status.value
        model.order = activity.order
        model.updated_at = activity.updated_at

    def update_status(self, activity_id: str, status: str) -> None:
        model = self.session.query(ActivityModel).filter_by(id=activity_id).first()
        if model:
            model.status = status
            self.session.commit()

    def find_by_id(self, activity_id: str) -> Optional[Activity]:
        model = self.session.query(ActivityModel).filter_by(id=activity_id).first()
        if not model:
            return None
        
        return Activity(
            id=model.id,
            course_id=model.course_id,
            teacher_id=model.teacher_id,
            title=model.title,
            description=model.description,
            type=ActivityType(model.type),
            status=ExerciseStatus(model.status),
            order=model.order,
            created_at=model.created_at,
            updated_at=model.updated_at
        )

    def list_by_course(self, course_id: str) -> List[Activity]:
        models = self.session.query(ActivityModel).filter_by(course_id=course_id).all()
        return [
            Activity(
                id=m.id,
                course_id=m.course_id,
                teacher_id=m.teacher_id,
                title=m.title,
                description=m.description,
                type=ActivityType(m.type),
                status=ExerciseStatus(m.status),
                order=m.order,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in models
        ]

    def list_by_teacher(self, teacher_id: str) -> List[Activity]:
        print(f"DEBUG: list_by_teacher called for {teacher_id}")
        models = self.session.query(ActivityModel).filter_by(teacher_id=teacher_id).all()
        print(f"DEBUG: Found {len(models)} activities")
        for m in models:
            print(f"DEBUG: Activity {m.id} type={m.type}")
        return [
            Activity(
                id=m.id,
                course_id=m.course_id,
                teacher_id=m.teacher_id,
                title=m.title,
                description=m.description,
                type=ActivityType(m.type),
                status=ExerciseStatus(m.status),
                order=m.order,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in models
        ]

    def find_all_published(self) -> List[Activity]:
        models = self.session.query(ActivityModel).filter(ActivityModel.status == "published").all()
        return [
            Activity(
                id=m.id,
                course_id=m.course_id,
                teacher_id=m.teacher_id,
                title=m.title,
                description=m.description,
                type=ActivityType(m.type),
                status=ExerciseStatus(m.status),
                order=m.order,
                created_at=m.created_at,
                updated_at=m.updated_at
            ) for m in models
        ]

    def add_student_to_module(self, module_id: str, student_id: str) -> None:
        from ..models.academic_models import EnrollmentModel
        # Check if already exists
        exists = self.session.query(EnrollmentModel).filter_by(
            module_id=module_id,
            student_id=student_id
        ).first()
        if not exists:
            enrollment = EnrollmentModel(
                module_id=module_id,
                student_id=student_id,
                status="active"
            )
            self.session.add(enrollment)
            self.session.flush()

    def remove_student_from_module(self, module_id: str, student_id: str) -> None:
        from ..models.academic_models import EnrollmentModel
        self.session.query(EnrollmentModel).filter_by(
            module_id=module_id, 
            student_id=student_id
        ).delete()
        self.session.flush()

    def get_assigned_students(self, module_id: str) -> List[str]:
        from ..models.academic_models import EnrollmentModel
        enrollments = self.session.query(EnrollmentModel).filter_by(
            module_id=module_id,
            status="active"
        ).all()
        return [e.student_id for e in enrollments]
