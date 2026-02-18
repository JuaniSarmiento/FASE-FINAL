from src.domain.governance.entities.incident import Incident, IncidentType, IncidentSeverity
from src.domain.governance.ports.incident_repository import IncidentRepository
from src.application.shared.unit_of_work import UnitOfWork
from src.application.governance.dtos.governance_dtos import ReportIncidentRequest, IncidentDTO

class ReportIncident:
    def __init__(self, incident_repository: IncidentRepository, uow: UnitOfWork):
        self.incident_repository = incident_repository
        self.uow = uow

    def execute(self, request: ReportIncidentRequest) -> IncidentDTO:
        try:
            inc_type = IncidentType(request.incident_type)
            inc_severity = IncidentSeverity(request.severity)
        except ValueError as e:
            raise ValueError(f"Invalid type or severity: {e}")

        incident = Incident.create(
            student_id=request.student_id,
            incident_type=inc_type,
            description=request.description,
            severity=inc_severity
        )
        
        with self.uow:
            self.incident_repository.save(incident)
            
        return IncidentDTO(
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
