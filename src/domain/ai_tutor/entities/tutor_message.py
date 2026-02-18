from dataclasses import dataclass, field
from datetime import datetime
from src.domain.shared.entity import Entity
from ..value_objects.message_role import MessageRole

@dataclass
class TutorMessage(Entity):
    session_id: str
    role: MessageRole
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
