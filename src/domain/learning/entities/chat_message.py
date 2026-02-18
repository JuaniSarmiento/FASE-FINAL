from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from src.domain.shared.entity import Entity

class MessageSender(str, Enum):
    STUDENT = "student"
    AI_TUTOR = "ai_tutor"
    SYSTEM = "system"

@dataclass(kw_only=True)
class ChatMessage(Entity):
    session_id: str
    content: str
    sender: MessageSender
    created_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def create(cls, id: str, session_id: str, content: str, sender: MessageSender) -> 'ChatMessage':
        return cls(
            id=id,
            session_id=session_id,
            content=content,
            sender=sender
        )
