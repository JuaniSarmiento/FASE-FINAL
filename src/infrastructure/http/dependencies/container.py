from fastapi import Depends
from sqlalchemy.orm import Session
from src.infrastructure.persistence.database import get_db
from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
from src.infrastructure.persistence.repositories.exercise_repository_impl import SqlAlchemyExerciseRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork
from src.infrastructure.ai.llm.ollama_service import OllamaExerciseGenerator
from src.application.learning.commands.generate_exercises import GenerateExercises
from src.infrastructure.persistence.repositories.user_repository_impl import SqlAlchemyUserRepository
from src.infrastructure.auth.bcrypt_hasher import BcryptHasher
from src.infrastructure.auth.jwt_token_provider import JwtTokenProvider
from src.application.identity.commands.register_user import RegisterUser
from src.application.identity.commands.authenticate_user import AuthenticateUser

from src.application.identity.commands.authenticate_user import AuthenticateUser
from src.infrastructure.persistence.repositories.session_repository_impl import SqlAlchemySessionRepository
from src.infrastructure.persistence.repositories.submission_repository_impl import SqlAlchemySubmissionRepository
from src.infrastructure.grading.local_code_executor import LocalCodeExecutor
from src.application.student.queries.list_activities import ListStudentActivities
from src.application.student.commands.start_session import StartLearningSession
from src.application.student.commands.send_message import SendMessageToTutor
from src.application.student.commands.submit_solution import SubmitSolution

def get_exercise_generator():
    return OllamaExerciseGenerator()

def get_activity_repository(db: Session = Depends(get_db)):
    return SqlAlchemyActivityRepository(db)

def get_exercise_repository(db: Session = Depends(get_db)):
    return SqlAlchemyExerciseRepository(db)

def get_unit_of_work(db: Session = Depends(get_db)):
    # SqlAlchemyUnitOfWork expects a session_factory, but for per-request dependency 
    # we might need to adapt. 
    # A cleaner approach for FastAPI is to use the session directly or a UoW that wraps the session.
    # For now, let's create a UoW that takes the session factory for consistency with the pattern,
    # or better yet, adapt UoW to consume the active session.
    # HOWEVER, the UoW in Application expects specific methods.
    
    # ADAPTATION: We will inject a UoW that manages the *current* session transaction.
    return SqlAlchemyUnitOfWork(lambda: db) 

from src.infrastructure.persistence.repositories.document_repository_impl import SqlAlchemyDocumentRepository
from src.infrastructure.ai.rag.rag_service import RagService
from src.application.learning.commands.upload_document_command import UploadDocumentCommand
from src.application.learning.commands.chat_with_document_command import ChatWithDocumentCommand

def get_document_repository(db: Session = Depends(get_db)):
    return SqlAlchemyDocumentRepository(db)

def get_rag_service(doc_repo = Depends(get_document_repository)):
    return RagService(document_repository=doc_repo)

def get_upload_document_command(rag_service = Depends(get_rag_service)):
    return UploadDocumentCommand(rag_service=rag_service)

def get_chat_with_document_command(rag_service = Depends(get_rag_service)):
    return ChatWithDocumentCommand(rag_service=rag_service)

def get_generate_exercises_use_case(
    generator = Depends(get_exercise_generator),
    activity_repo = Depends(get_activity_repository),
    exercise_repo = Depends(get_exercise_repository),
    doc_repo = Depends(get_document_repository),
    uow = Depends(get_unit_of_work)
):
    return GenerateExercises(
        exercise_generator=generator,
        exercise_repository=exercise_repo,
        activity_repository=activity_repo,
        document_repository=doc_repo,
        unit_of_work=uow
    )

def get_user_repository(db: Session = Depends(get_db)):
    return SqlAlchemyUserRepository(db)

def get_password_hasher():
    return BcryptHasher()

def get_token_provider():
    return JwtTokenProvider()

def get_register_use_case(
    user_repo = Depends(get_user_repository),
    hasher = Depends(get_password_hasher),
    token_provider = Depends(get_token_provider),
    uow = Depends(get_unit_of_work)
):
    return RegisterUser(
        user_repository=user_repo,
        password_hasher=hasher,
        token_provider=token_provider,
        unit_of_work=uow
    )

def get_authenticate_use_case(
    user_repo = Depends(get_user_repository),
    hasher = Depends(get_password_hasher),
    token_provider = Depends(get_token_provider),
    uow = Depends(get_unit_of_work)
):
    return AuthenticateUser(
        user_repository=user_repo,
        password_hasher=hasher,
        token_provider=token_provider,
        unit_of_work=uow
    )

def get_session_repository(db: Session = Depends(get_db)):
    return SqlAlchemySessionRepository(db)

def get_submission_repository(db: Session = Depends(get_db)):
    return SqlAlchemySubmissionRepository(db)

from src.infrastructure.persistence.repositories.enrollment_repository_impl import SqlAlchemyEnrollmentRepository

def get_enrollment_repository(db: Session = Depends(get_db)):
    return SqlAlchemyEnrollmentRepository(db)

def get_code_executor():
    return LocalCodeExecutor()

from src.infrastructure.ai.llm.ollama_auditor import OllamaAuditor

def get_ai_auditor():
    return OllamaAuditor()

def get_list_activities_query(repo = Depends(get_activity_repository)):
    return ListStudentActivities(activity_repository=repo)

from src.application.student.queries.list_courses import ListStudentCourses

def get_list_courses_query(
    act_repo = Depends(get_activity_repository),
    enroll_repo = Depends(get_enrollment_repository)
):
    return ListStudentCourses(activity_repository=act_repo, enrollment_repository=enroll_repo)

from src.application.student.queries.get_activity_details import GetActivityDetails

def get_activity_details_query(
    act_repo = Depends(get_activity_repository),
    ex_repo = Depends(get_exercise_repository)
):
    return GetActivityDetails(act_repo, ex_repo)

def get_start_session_use_case(
    session_repo = Depends(get_session_repository),
    activity_repo = Depends(get_activity_repository),
    uow = Depends(get_unit_of_work)
):
    return StartLearningSession(
        session_repository=session_repo,
        activity_repository=activity_repo,
        unit_of_work=uow
    )

def get_send_message_use_case(
    session_repo = Depends(get_session_repository),
    ex_repo = Depends(get_exercise_repository),
    rag_service = Depends(get_rag_service), 
    uow = Depends(get_unit_of_work)
):
    return SendMessageToTutor(
        session_repository=session_repo,
        exercise_repository=ex_repo,
        rag_service=rag_service,
        unit_of_work=uow
    )

def get_submit_solution_use_case(
    sub_repo = Depends(get_submission_repository),
    ex_repo = Depends(get_exercise_repository),
    executor = Depends(get_code_executor),
    auditor = Depends(get_ai_auditor),
    uow = Depends(get_unit_of_work)
):
    return SubmitSolution(
        submission_repository=sub_repo,
        exercise_repository=ex_repo,
        code_executor=executor,
        ai_auditor=auditor,
        unit_of_work=uow
    )

from src.application.learning.commands.create_activity_command import CreateActivityCommand
from src.application.learning.queries.list_teacher_activities_query import ListTeacherActivitiesQuery

def get_create_activity_command(
    repo = Depends(get_activity_repository),
    uow = Depends(get_unit_of_work)
):
    return CreateActivityCommand(activity_repository=repo, unit_of_work=uow)

def get_list_teacher_activities_query(repo = Depends(get_activity_repository)):
    return ListTeacherActivitiesQuery(activity_repository=repo)



from src.application.learning.commands.publish_activity_command import PublishActivityCommand

def get_publish_activity_command(
    repo = Depends(get_activity_repository),
    uow = Depends(get_unit_of_work)
):
    return PublishActivityCommand(activity_repository=repo, unit_of_work=uow)



from src.infrastructure.persistence.repositories.submission_read_repository_impl import SqlAlchemySubmissionReadRepository

def get_submission_read_repository(db: Session = Depends(get_db)):
    return SqlAlchemySubmissionReadRepository(db)

from src.application.teacher.queries.get_student_activity_details import GetStudentActivityDetails

def get_student_activity_details_query(
    repo = Depends(get_submission_read_repository)
):
    return GetStudentActivityDetails(repository=repo)
