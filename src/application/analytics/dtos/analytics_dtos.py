from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from src.application.shared.dtos.common import DTO
from datetime import datetime

@dataclass
class CreateRiskAnalysisRequest(DTO):
    student_id: str

@dataclass
class RiskAnalysisDTO(DTO):
    id: str
    student_id: str
    risk_score: float
    risk_factors: List[str]
    details: Dict[str, Any]
    created_at: datetime
