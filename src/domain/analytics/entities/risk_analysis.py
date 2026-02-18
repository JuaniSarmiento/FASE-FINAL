from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any
from src.domain.shared.entity import Entity

@dataclass(kw_only=True)
@dataclass(kw_only=True)
class RiskAnalysis(Entity):
    submission_id: str
    risk_score: int # 0 to 100
    risk_level: str
    diagnosis: str
    evidence: List[str] = field(default_factory=list)
    teacher_advice: str
    positive_aspects: List[str] = field(default_factory=list)
    analyzed_at: datetime = field(default_factory=datetime.utcnow)

    @classmethod
    def create(cls, submission_id: str, risk_score: int, risk_level: str, diagnosis: str, evidence: List[str], teacher_advice: str, positive_aspects: List[str]) -> 'RiskAnalysis':
        return cls(
            submission_id=submission_id,
            risk_score=risk_score,
            risk_level=risk_level,
            diagnosis=diagnosis,
            evidence=evidence,
            teacher_advice=teacher_advice,
            positive_aspects=positive_aspects
        )
