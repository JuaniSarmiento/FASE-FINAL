from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.governance.ports.incident_repository import IncidentRepository
from src.domain.governance.entities.incident import Incident, IncidentType, IncidentSeverity, IncidentStatus
from src.infrastructure.persistence.models.governance_models import IncidentModel

class SqlAlchemyIncidentRepository(IncidentRepository):
    def __init__(self, db: Session):
        self.db = db

    def save(self, incident: Incident) -> None:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident.id).first()
        if not model:
            model = IncidentModel(
                id=incident.id,
                student_id=incident.student_id,
                incident_type=incident.incident_type.value,
                description=incident.description,
                severity=incident.severity.value,
                status=incident.status.value,
                created_at=incident.created_at,
                resolved_at=incident.resolved_at,
                resolution_notes=incident.resolution_notes
            )
            self.db.add(model)
        else:
            model.status = incident.status.value
            model.resolved_at = incident.resolved_at
            model.resolution_notes = incident.resolution_notes

    def find_by_id(self, incident_id: str) -> Optional[Incident]:
        model = self.db.query(IncidentModel).filter(IncidentModel.id == incident_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def list_by_student(self, student_id: str) -> List[Incident]:
        models = self.db.query(IncidentModel).filter(IncidentModel.student_id == student_id).all()
        return [self._to_entity(m) for m in models]

    def list_all(self) -> List[Incident]:
        models = self.db.query(IncidentModel).all()
        return [self._to_entity(m) for m in models]
        
    def _to_entity(self, model: IncidentModel) -> Incident:
        incident = Incident(
            id=model.id,
            student_id=model.student_id,
            incident_type=IncidentType(model.incident_type),
            description=model.description,
            severity=IncidentSeverity(model.severity),
            status=IncidentStatus(model.status),
            created_at=model.created_at,
            resolved_at=model.resolved_at,
            resolution_notes=model.resolution_notes
        )
        return incident
