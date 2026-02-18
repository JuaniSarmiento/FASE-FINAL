from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.domain.shared.entity import Entity

class IncidentSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IncidentStatus(str, Enum):
    OPEN = "open"
    INVESTIGATING = "investigating"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"

class IncidentType(str, Enum):
    ACADEMIC_INTEGRITY = "academic_integrity"
    AI_DEPENDENCY = "ai_dependency"
    WELLBEING = "wellbeing"
    OTHER = "other"

@dataclass(kw_only=True)
class Incident(Entity):
    student_id: str
    incident_type: IncidentType
    description: str
    severity: IncidentSeverity = IncidentSeverity.LOW
    status: IncidentStatus = IncidentStatus.OPEN
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: datetime = None
    resolution_notes: str = ""

    @classmethod
    def create(cls, student_id: str, incident_type: IncidentType, description: str, severity: IncidentSeverity) -> 'Incident':
        return cls(
            student_id=student_id,
            incident_type=incident_type,
            description=description,
            severity=severity
        )

    def resolve(self, notes: str) -> None:
        self.status = IncidentStatus.RESOLVED
        self.resolution_notes = notes
        self.resolved_at = datetime.utcnow()
