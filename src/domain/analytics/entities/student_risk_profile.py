from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from src.domain.shared.entity import Entity
from ..value_objects.risk_level import RiskLevel

@dataclass
class StudentRiskProfile(Entity):
    student_id: str
    risk_score: float = 0.0
    risk_level: RiskLevel = RiskLevel.LOW
    risk_factors: Dict[str, Any] = field(default_factory=dict)
    last_updated: datetime = field(default_factory=datetime.now)
    
    def update_risk(self, score: float, level: RiskLevel, factors: Dict[str, Any]) -> None:
        self.risk_score = score
        self.risk_level = level
        self.risk_factors = factors
        self.last_updated = datetime.now()
