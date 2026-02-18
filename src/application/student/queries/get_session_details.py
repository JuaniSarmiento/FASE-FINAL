from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from src.application.shared.dtos.common import DTO
from src.domain.learning.ports.session_repository import SessionRepository

@dataclass
class ChatMessageDTO(DTO):
    id: str
    content: str
    sender: str
    created_at: datetime

@dataclass
class SessionDetailsDTO(DTO):
    session_id: str
    student_id: str
    activity_id: str
    status: str
    start_time: datetime
    messages: List[ChatMessageDTO]

class GetSessionDetails:
    def __init__(self, session_repository: SessionRepository):
        self.session_repository = session_repository

    def execute(self, session_id: str) -> Optional[SessionDetailsDTO]:
        session = self.session_repository.find_by_id(session_id)
        if not session:
            return None
        
        # Map messages
        messages_dto = [
            ChatMessageDTO(
                id=str(m.id),
                content=m.content,
                sender=m.sender.value,
                created_at=m.created_at
            )
            for m in session.messages
        ]
        
        return SessionDetailsDTO(
            session_id=str(session.id),
            student_id=session.student_id,
            activity_id=session.activity_id,
            status=session.status.value,
            start_time=session.start_time,
            messages=messages_dto
        )
