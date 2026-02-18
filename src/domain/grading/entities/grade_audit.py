from dataclasses import dataclass, field
from datetime import datetime
from src.domain.shared.entity import Entity
from ..value_objects.score import Score

@dataclass
class GradeAudit(Entity):
    submission_id: str
    grader_id: str
    previous_score: Score
    new_score: Score
    reason: str
    timestamp: datetime = field(default_factory=datetime.now)
