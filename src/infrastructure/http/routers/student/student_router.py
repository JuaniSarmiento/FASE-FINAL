from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
import logging
import traceback
from src.application.student.queries.list_activities import ListStudentActivities, ActivitySummaryDTO
from src.application.student.commands.start_session import StartLearningSession, StartSessionRequest
from src.application.student.commands.send_message import SendMessageToTutor, SendMessageRequest, TutorMessageDTO
from src.application.student.commands.submit_solution import SubmitSolution, SubmitSolutionRequest, SubmitSolutionResponse
from src.application.student.queries.list_courses import ListStudentCourses, CourseSummaryDTO
from src.infrastructure.http.dependencies.container import (
    get_list_activities_query,
    get_start_session_use_case,
    get_send_message_use_case,
    get_submit_solution_use_case,
    get_list_courses_query,
    get_session_repository
)
from src.domain.learning.ports.session_repository import SessionRepository
from src.application.student.queries.get_session_details import GetSessionDetails, SessionDetailsDTO
from src.application.student.queries.list_grades import ListStudentGrades, GradeDTO
from src.infrastructure.persistence.database import get_db
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/courses", response_model=List[CourseSummaryDTO])
def list_courses(
    student_id: str = "default_student", # Mock auth for now or from token
    query: ListStudentCourses = Depends(get_list_courses_query)
):
    # In a real app, extract student_id from token
    # For now, we might receive it as query param or generic default
    # But current auth middleware should inject "current_user"
    return query.execute(student_id)

@router.get("/activities", response_model=List[ActivitySummaryDTO])
def list_activities(
    student_id: str = "default_student", # Mock auth for now or from token
    use_case: ListStudentActivities = Depends(get_list_activities_query)
):
    return use_case.execute(student_id)

from src.application.student.queries.get_activity_details import GetActivityDetails, ActivityDetailsDTO
from src.infrastructure.http.dependencies.container import get_activity_details_query

@router.get("/activities/{activity_id}", response_model=ActivityDetailsDTO)
def get_activity_details(
    activity_id: str,
    query: GetActivityDetails = Depends(get_activity_details_query)
):
    result = query.execute(activity_id)
    if not result:
        raise HTTPException(status_code=404, detail="Activity not found")
    return result

@router.post("/sessions", status_code=status.HTTP_201_CREATED)
def start_session(
    request: StartSessionRequest,
    use_case: StartLearningSession = Depends(get_start_session_use_case)
):
    try:
        session = use_case.execute(request)
        return {"session_id": str(session.id), "status": session.status.value} # Return simplified DTO or Entity
        # LearningSession entity is not Pydantic model, so fastAPI cant serialize it directly if response_model is not set or custom encoder.
        # Returning dict for simplicity.
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/sessions/{session_id}/chat", response_model=TutorMessageDTO)
def send_message(
    session_id: str,
    request: SendMessageRequest,
    use_case: SendMessageToTutor = Depends(get_send_message_use_case)
):
    request.session_id = session_id # Ensure ID from path
    try:
        return use_case.execute(request)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

from pydantic import BaseModel
from typing import Optional, Dict

class CodeSubmissionBody(BaseModel):
    code: str
    exercise_id: Optional[str] = None
    is_final_submission: bool = False
    all_exercise_codes: Optional[Dict[str, str]] = None
    language: str = "python"

@router.post("/sessions/{session_id}/submit", response_model=SubmitSolutionResponse)
def submit_solution(
    session_id: str,
    body: CodeSubmissionBody,
    use_case: SubmitSolution = Depends(get_submit_solution_use_case),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    # 1. Fetch Session to get student_id and activity_id
    session = session_repo.find_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # 2. Construct Request Object for Use Case
    request = SubmitSolutionRequest(
        session_id=session_id,
        student_id=session.student_id,
        activity_id=session.activity_id,
        code=body.code,
        exercise_id=body.exercise_id,
        language=body.language,
        is_final_submission=body.is_final_submission,
        all_exercise_codes=body.all_exercise_codes
    )

    try:
        return use_case.execute(request)
    except Exception as e:
        logger.error(f"Error submitting solution: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/sessions/{session_id}", response_model=SessionDetailsDTO)
def get_session_details(
    session_id: str,
    repository: SessionRepository = Depends(get_session_repository)
):
    query = GetSessionDetails(repository)
    result = query.execute(session_id)
    if not result:
        raise HTTPException(status_code=404, detail="Session not found")
    return result

@router.get("/grades", response_model=List[GradeDTO])
def list_grades(
    student_id: str = "default_student",
    db: Session = Depends(get_db)
):
    query = ListStudentGrades(db)
    return query.execute(student_id)
