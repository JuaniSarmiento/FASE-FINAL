import sys
import os
import uuid
import time
sys.path.append(os.getcwd())

from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.session_repository_impl import SqlAlchemySessionRepository
from src.infrastructure.persistence.repositories.document_repository_impl import SqlAlchemyDocumentRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.ai.rag.rag_service import RagService
from src.application.student.commands.send_message import SendMessageToTutor, SendMessageRequest
from src.domain.learning.entities.session import LearningSession, SessionStatus
from src.domain.learning.entities.chat_message import MessageSender

def test_chat_persistence():
    print("--- Testing Chat Persistence & RAG ---")
    db = next(get_db())
    session_repo = SqlAlchemySessionRepository(db)
    doc_repo = SqlAlchemyDocumentRepository(db)
    rag_service = RagService(doc_repo)
    uow = SqlAlchemyUnitOfWork(lambda: db)
    
    command = SendMessageToTutor(session_repo, rag_service, uow)
    
    # Setup Data
    student_id = "test_student_chat"
    activity_id = "test_activity_chat" # Ideally one that has documents, but empty is fine for persistence test
    
    # 1. Create Session
    session_id = str(uuid.uuid4())
    print(f"Creating Session {session_id}...")
    session = LearningSession(
        id=session_id,
        student_id=student_id,
        activity_id=activity_id,
        status=SessionStatus.ACTIVE
    )
    with uow:
        session_repo.save(session)
        uow.commit() # Save initial session
        
    # 2. Send Message
    msg_content = "Hola, ¿cómo puedo imprimir en Python?"
    print(f"Sending Message: '{msg_content}'")
    
    request = SendMessageRequest(
        session_id=session_id,
        message=msg_content,
        code_context="print('hi')"
    )
    
    try:
        response = command.execute(request)
        print(f"AI Response: {response.content}")
    except Exception as e:
        print(f"Error executing command: {e}")
        # If RAG fails (e.g. no connection), persistence might fail if not handled? 
        # Command executes logical flow.
        return

    # 3. Verify Persistence
    print("Verifying persistence...")
    db.expire_all()
    
    loaded_session = session_repo.find_by_id(session_id)
    if not loaded_session:
        print("ERROR: Session not found after save!")
        return
        
    print(f"Loaded Session Messages: {len(loaded_session.messages)}")
    for m in loaded_session.messages:
        print(f" - [{m.sender}]: {m.content[:50]}...")
        
    if len(loaded_session.messages) >= 2:
        print("SUCCESS: User and AI messages persisted.")
    else:
        print("FAILURE: Messages not persisted correctly.")

if __name__ == "__main__":
    test_chat_persistence()
