from dataclasses import dataclass
from typing import Optional
from src.application.shared.dtos.common import DTO
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.learning.ports.session_repository import SessionRepository
import uuid
from src.domain.learning.entities.chat_message import ChatMessage, MessageSender
from src.domain.ai.ports.rag_service import RagServicePort

from src.domain.learning.ports.exercise_repository import ExerciseRepository

@dataclass
class SendMessageRequest(DTO):
    session_id: str
    message: str
    code_context: Optional[str] = None
    exercise_id: Optional[str] = None

@dataclass
class TutorMessageDTO(DTO):
    content: str
    sender: str = "ai_tutor"

class SendMessageToTutor:
    def __init__(
        self,
        session_repository: SessionRepository,
        exercise_repository: ExerciseRepository,
        rag_service: RagServicePort,
        unit_of_work: UnitOfWork
    ):
        self.session_repository = session_repository
        self.exercise_repository = exercise_repository
        self.rag_service = rag_service
        self.unit_of_work = unit_of_work

    def execute(self, request: SendMessageRequest) -> TutorMessageDTO:
        session = self.session_repository.find_by_id(request.session_id)
        if not session:
            raise ValueError("Session not found")

        # 1. Add User Message
        user_msg = ChatMessage.create(
            id=str(uuid.uuid4()),
            session_id=str(session.id),
            content=request.message,
            sender=MessageSender.STUDENT
        )
        session.add_message(user_msg)

        # 2. Retrieve Context (RAG) & Exercise Details
        activity_id = session.activity_id
        
        # Retrieve relevant docs
        docs = self.rag_service.query(activity_id, request.message)
        context_str = "\n".join(docs)
        
        # Retrieve Exercise Details if exercise_id provided
        problem_statement = ""
        solution_code = ""
        
        if request.exercise_id:
            exercise = self.exercise_repository.find_by_id(request.exercise_id)
            if exercise:
                problem_statement = exercise.problem_statement
                solution_code = exercise.solution_code or "No solution code provided."
        
        # 3. Prepare History
        history = [
            {"role": "user" if m.sender == MessageSender.STUDENT else "assistant", "content": m.content}
            for m in session.messages
        ]
        
        # 4. Generate AI Response
        ai_response_text = self.rag_service.generate_tutor_response(
            query=request.message,
            context=context_str,
            history=history,
            code_context=request.code_context,
            problem_statement=problem_statement,
            solution_code=solution_code
        )
        
        # 5. Add AI Message
        ai_msg = ChatMessage.create(
            id=str(uuid.uuid4()),
            session_id=str(session.id),
            content=ai_response_text,
            sender=MessageSender.AI_TUTOR
        )
        session.add_message(ai_msg)
        
        # 6. Save Session (persists messages via Cascade/Repository logic)
        try:
            with self.unit_of_work:
                self.session_repository.save(session)
                self.unit_of_work.commit()
        except Exception as e:
            import traceback
            print(f"CRITICAL ERROR saving session/messages: {e}")
            traceback.print_exc()
            raise e
            
        return TutorMessageDTO(content=ai_response_text)
