from dataclasses import dataclass
from typing import Optional
from src.application.shared.dtos.common import DTO
from datetime import datetime

@dataclass
class ReportIncidentRequest(DTO):
    student_id: str
    incident_type: str
    description: str
    severity: str = "low"

@dataclass
class ResolveIncidentRequest(DTO):
    incident_id: str
    notes: str

@dataclass
class IncidentDTO(DTO):
    id: str
    student_id: str
    incident_type: str
    description: str
    severity: str
    status: str
    created_at: datetime
    resolved_at: Optional[datetime] = None
    resolution_notes: str = ""
