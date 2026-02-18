from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional
from src.domain.shared.entity import AggregateRoot
from ..value_objects.tutor_mode import TutorMode
from ..value_objects.cognitive_phase import CognitivePhase
from .tutor_message import TutorMessage

@dataclass
class TutorSession(AggregateRoot):
    student_id: str
    activity_id: str
    status: str = "active"
    mode: TutorMode = TutorMode.SOCRATIC
    current_phase: CognitivePhase = CognitivePhase.ENGAGEMENT
    messages: List[TutorMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    def add_message(self, message: TutorMessage) -> None:
        self.messages.append(message)
        self.updated_at = datetime.now()
        
    def end_session(self) -> None:
        self.status = "completed"
        self.updated_at = datetime.now()
