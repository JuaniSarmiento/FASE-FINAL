from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from src.domain.shared.entity import AggregateRoot
from ..value_objects.session_status import SessionStatus

@dataclass(kw_only=True)
class LearningSession(AggregateRoot):
    student_id: str
    activity_id: str
    status: SessionStatus = SessionStatus.ACTIVE
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    
    messages: list['ChatMessage'] = field(default_factory=list)

    def add_message(self, message: 'ChatMessage') -> None:
        self.messages.append(message)
        self.updated_at = datetime.now()

    def complete(self) -> None:
        self.status = SessionStatus.COMPLETED
        self.end_time = datetime.now()
        
    def abandon(self) -> None:
        self.status = SessionStatus.ABANDONED
        self.end_time = datetime.now()

