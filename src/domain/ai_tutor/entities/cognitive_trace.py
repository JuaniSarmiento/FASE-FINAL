from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional
from src.domain.shared.entity import Entity

@dataclass
class CognitiveTrace(Entity):
    session_id: str
    student_id: str
    activity_id: str
    content: str
    interaction_type: str
    trace_level: str = "N4_COGNITIVO"
    cognitive_state: Optional[str] = None
    cognitive_intent: Optional[str] = None
    decision_justification: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
