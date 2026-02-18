from typing import List, Optional
from sqlalchemy.orm import Session
from src.domain.learning.ports.session_repository import SessionRepository
from src.domain.learning.entities.session import LearningSession
from src.domain.learning.value_objects.session_status import SessionStatus
from src.infrastructure.persistence.models.learning_models import SessionModel
from src.infrastructure.persistence.models.ai_tutor_models import TutorMessageModel
from src.domain.learning.entities.chat_message import ChatMessage, MessageSender

class SqlAlchemySessionRepository(SessionRepository):
    def __init__(self, db_session: Session):
        self.db_session = db_session

    def save(self, session: LearningSession) -> None:
        model = self.db_session.query(SessionModel).filter(SessionModel.id == str(session.id)).first()
        if not model:
            model = SessionModel(
                id=str(session.id),
                student_id=session.student_id,
                activity_id=session.activity_id,
                status=session.status.value,
                start_time=session.start_time,
                end_time=session.end_time
            )
            self.db_session.add(model)
        else:
            model.status = session.status.value
            model.end_time = session.end_time
            model.updated_at = session.updated_at
        
        # Sync Messages
        # For simplicity, we add messages that are not yet in DB. 
        # Assuming ID consistency.
        # Ideally we might wipe and recreate or diff, but here we just ensure they exist.
        
        # We need to flush/commit the session model first to ensure it's attached? 
        # No, adding to model.messages should work if model is attached.
        
        current_msg_ids = {m.id for m in model.messages}
        for msg in session.messages:
            if str(msg.id) not in current_msg_ids:
                new_msg = TutorMessageModel(
                    id=str(msg.id),
                    session_id=str(session.id),
                    role=msg.sender.value,
                    content=msg.content,
                    created_at=msg.created_at
                )
                model.messages.append(new_msg)

    def find_by_id(self, session_id: str) -> Optional[LearningSession]:
        model = self.db_session.query(SessionModel).filter(SessionModel.id == session_id).first()
        if not model:
            return None
        return self._to_entity(model)

    def list_by_student(self, student_id: str) -> List[LearningSession]:
        models = self.db_session.query(SessionModel).filter(SessionModel.student_id == student_id).all()
        return [self._to_entity(m) for m in models]

    def find_active_by_student(self, student_id: str) -> Optional[LearningSession]:
        model = self.db_session.query(SessionModel).filter(
            SessionModel.student_id == student_id,
            SessionModel.status == SessionStatus.ACTIVE.value
        ).first()
        if model:
            return self._to_entity(model)
        return None

    def _to_entity(self, model: SessionModel) -> LearningSession:
        try:
            status_enum = SessionStatus(model.status)
        except:
             status_enum = SessionStatus.ACTIVE
             
        session = LearningSession(
            id=model.id,
            student_id=model.student_id,
            activity_id=model.activity_id,
            status=status_enum,
            start_time=model.start_time,
            end_time=model.end_time
        )
        
        # Map messages
        # sort by created_at
        sorted_msgs = sorted(model.messages, key=lambda m: m.created_at)
        for m in sorted_msgs:
            try:
                sender = MessageSender(m.role)
            except:
                sender = MessageSender.SYSTEM # Fallback
                
            session.add_message(ChatMessage.create(
                id=m.id,
                session_id=model.id,
                content=m.content,
                sender=sender
            ))
            # Override created_at to match DB
            session.messages[-1].created_at = m.created_at
            
        return session
