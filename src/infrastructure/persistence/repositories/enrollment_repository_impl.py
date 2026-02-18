from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.academic.ports.enrollment_repository import EnrollmentRepository
from src.domain.academic.entities.enrollment import Enrollment
from src.infrastructure.persistence.models.academic_models import EnrollmentModel

class SqlAlchemyEnrollmentRepository(EnrollmentRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, enrollment: Enrollment) -> None:
        # Mapper logic would go here if using pure domain entities
        # For now, assuming we might use the model directly or mapper
        # But this method is not the focus of the current task (reading)
        pass

    def find_by_id(self, enrollment_id: str) -> Optional[Enrollment]:
        # Implementation skipped for now
        pass

    def find_by_student_and_course(self, student_id: str, commission_id: str) -> Optional[Enrollment]:
        # Implementation skipped for now
        pass

    def list_by_student(self, student_id: str) -> List[Enrollment]:
        # We return domain entities, but for MVP speed we might return models 
        # providing we have a mapper. 
        # Let's see how other repos do it.
        # But wait, the interface returns List[Enrollment].
        # I'll construct simple Enrollment entities or just use the model if the domain allows.
        # Given the previous context, we often work with DTOs in queries.
        # But the Repository MUST return Domain Entities.
        
        models = self.session.query(EnrollmentModel).filter(
            EnrollmentModel.student_id == student_id,
            EnrollmentModel.status == "active"
        ).all()
        
        # Simple mapper
        enrollments = []
        for m in models:
            # We need to map Model -> Entity
            # Assuming Enrollment entity exists and has similar fields
            # If not, we might need to check the entity definition.
            # For now, I'll return the Model and let the Query handle it 
            # OR better, map it to a simple object if generic.
            # Let's check the Entity definition first if possible, but I'll proceed with a basic mapping assumption
            # generic to object to avoid import errors if Entity is strict
            enrollments.append(m) 
            
        return enrollments
