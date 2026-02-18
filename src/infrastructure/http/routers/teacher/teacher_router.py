from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.teacher.queries.get_dashboard import GetTeacherDashboard, TeacherDashboardDTO
from src.application.teacher.queries.list_students import ListStudentsWithRisk, StudentRiskDTO
from src.infrastructure.http.dependencies.container import (
    get_user_repository,
    get_activity_repository,
    get_submission_repository,
    get_session_repository,
    get_exercise_repository
)

router = APIRouter()

@router.get("/dashboard", response_model=TeacherDashboardDTO)
def get_dashboard(
    user_repo = Depends(get_user_repository),
    activity_repo = Depends(get_activity_repository)
):
    query = GetTeacherDashboard(user_repo, activity_repo)
    return query.execute()

@router.get("/students", response_model=List[StudentRiskDTO])
def list_students(
    user_repo = Depends(get_user_repository),
    submission_repo = Depends(get_submission_repository),
    session_repo = Depends(get_session_repository)
):
    query = ListStudentsWithRisk(user_repo, submission_repo, session_repo)
    return query.execute()

from src.application.learning.dtos.activity_dtos import CreateActivityRequest, ActivityResponse
from src.application.learning.commands.create_activity_command import CreateActivityCommand
from src.application.learning.queries.list_teacher_activities_query import ListTeacherActivitiesQuery
from src.infrastructure.http.dependencies.container import get_create_activity_command, get_list_teacher_activities_query
from src.infrastructure.http.dependencies.auth import get_current_user_id

@router.post("/activities", response_model=ActivityResponse)
def create_activity(
    request: CreateActivityRequest,
    teacher_id: str = Depends(get_current_user_id),
    command: CreateActivityCommand = Depends(get_create_activity_command)
):
    return command.execute(request, teacher_id)

@router.get("/activities", response_model=List[ActivityResponse])
def list_teacher_activities(
    teacher_id: str = Depends(get_current_user_id),
    query: ListTeacherActivitiesQuery = Depends(get_list_teacher_activities_query)
):
    return query.execute(teacher_id)

@router.get("/activities/{activity_id}", response_model=ActivityResponse)
def get_activity(
    activity_id: str,
    activity_repo = Depends(get_activity_repository),
    exercise_repo = Depends(get_exercise_repository)
):
    activity = activity_repo.find_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    return ActivityResponse(
        id=activity.id,
        course_id=activity.course_id,
        teacher_id=activity.teacher_id,
        title=activity.title,
        description=activity.description,
        type=activity.type.value,
        status=activity.status.value,
        order=activity.order,
        created_at=activity.created_at,
        updated_at=activity.updated_at,
        exercise_count=exercise_repo.count_by_activity(activity.id)
    )





from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime

class ExerciseResponse(BaseModel):
    id: str
    activity_id: str
    title: str
    problem_statement: str
    starter_code: str
    difficulty: str
    language: str
    status: str
    test_cases: List[dict]
    created_at: datetime
    updated_at: datetime

@router.get("/activities/{activity_id}/exercises", response_model=List[ExerciseResponse])
def get_activity_exercises(
    activity_id: str,
    exercise_repo = Depends(get_exercise_repository)
):
    exercises = exercise_repo.list_by_activity(activity_id) or []
    return [
        ExerciseResponse(
            id=ex.id,
            activity_id=ex.activity_id,
            title=ex.title,
            problem_statement=ex.problem_statement,
            starter_code=ex.starter_code,
            difficulty=ex.difficulty.value,
            language=ex.language.value,
            status=ex.status.value,
            test_cases=[
                {
                    "input_data": tc.input_data,
                    "expected_output": tc.expected_output,
                    "is_hidden": tc.is_hidden,
                    "weight": tc.weight
                } for tc in ex.test_cases
            ],
            created_at=ex.created_at,
            updated_at=ex.updated_at
        ) for ex in exercises
    ]

@router.get("/modules/{module_id}/activities", response_model=List[ActivityResponse])
def get_module_activities(
    module_id: str,
    activity_repo = Depends(get_activity_repository),
    exercise_repo = Depends(get_exercise_repository)
):
    # We use list_by_course because we are using module_id as the course_id link
    activities = activity_repo.list_by_course(module_id)
    return [
        ActivityResponse(
            id=a.id,
            course_id=a.course_id,
            teacher_id=a.teacher_id,
            title=a.title,
            description=a.description,
            type=a.type,
            status=a.status,
            order=a.order,
            created_at=a.created_at,
            updated_at=a.updated_at,
            exercise_count=exercise_repo.count_by_activity(a.id)
        ) for a in activities
    ]

from src.application.learning.commands.publish_activity_command import PublishActivityCommand
from src.infrastructure.http.dependencies.container import get_publish_activity_command

class PublishActivityRequest(BaseModel):
    course_id: Optional[str] = None

@router.post("/activities/{activity_id}/publish")
def publish_activity(
    activity_id: str,
    request: PublishActivityRequest = None,
    command: PublishActivityCommand = Depends(get_publish_activity_command)
):
    print(f"DEBUG: Endpoint /publish hit for {activity_id}")
    course_id = request.course_id if request else None
    print(f"DEBUG: Request Payload: {request}")
    command.execute(activity_id, course_id)
    return {"message": "Activity published successfully"}

class ActivityStatusUpdate(BaseModel):
    status: str

@router.patch("/activities/{activity_id}/status")
def update_activity_status(
    activity_id: str,
    request: ActivityStatusUpdate,
    activity_repo = Depends(get_activity_repository)
):
    activity = activity_repo.find_by_id(activity_id)
    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")
    
    # Validate status (simple validation)
    if request.status not in ["published", "draft", "archived"]:
        raise HTTPException(status_code=400, detail="Invalid status")

    activity_repo.update_status(activity_id, request.status)
    return {"message": "Status updated successfully", "status": request.status}


from src.application.teacher.dtos.student_dto import StudentDTO, AddStudentsRequest
from src.application.teacher.queries.get_module_students import GetModuleStudentsQuery
from src.application.teacher.commands.add_students_to_module import AddStudentsToModuleCommand
from src.application.teacher.commands.remove_student_from_module import RemoveStudentFromModuleCommand
from src.infrastructure.http.dependencies.container import get_unit_of_work

@router.get("/modules/{module_id}/students", response_model=List[StudentDTO])
def get_module_students(
    module_id: str,
    activity_repo = Depends(get_activity_repository),
    user_repo = Depends(get_user_repository)
):
    query = GetModuleStudentsQuery(activity_repo, user_repo)
    return query.execute(module_id)

@router.post("/modules/{module_id}/students")
def add_students_to_module(
    module_id: str,
    request: AddStudentsRequest,
    activity_repo = Depends(get_activity_repository),
    uow = Depends(get_unit_of_work)
):
    command = AddStudentsToModuleCommand(activity_repo, uow)
    command.execute(module_id, request.student_ids)
    return {"message": "Students added successfully"}

    command = RemoveStudentFromModuleCommand(activity_repo, uow)
    command.execute(module_id, student_id)
    return {"message": "Student removed successfully"}


# --- Analytics & Inspection Endpoints ---

from src.application.teacher.queries.get_student_activity_details import GetStudentActivityDetails, StudentActivityDetailsDTO
from src.infrastructure.ai.llm.risk_analyzer import RiskAnalyzer
from src.infrastructure.http.dependencies.container import get_student_activity_details_query
from src.infrastructure.persistence.database import get_db
from sqlalchemy.orm import Session

@router.get("/activities/{activity_id}/students/{student_id}/details", response_model=StudentActivityDetailsDTO)
def get_student_activity_details(
    activity_id: str,
    student_id: str,
    query: GetStudentActivityDetails = Depends(get_student_activity_details_query)
):
    result = query.execute(activity_id, student_id)
    if not result:
        raise HTTPException(status_code=404, detail="Student activity details not found")
    return result

@router.post("/activities/{activity_id}/students/{student_id}/analyze")
def analyze_student_risk(
    activity_id: str,
    student_id: str,
    query: GetStudentActivityDetails = Depends(get_student_activity_details_query)
):
    # Endpoint deprecated for frontend use, kept for internal debug or fallback
    # 1. Fetch Data
    details = query.execute(activity_id, student_id)
    if not details:
        raise HTTPException(status_code=404, detail="Details not found")

    # 2. Analyze with LLM
    analyzer = RiskAnalyzer() 
    
    analysis = analyzer.analyze_student_risk(
        student_name=student_id,
        activity_title=details.activity_title,
        chat_history=details.chat_history,
        code_submission=details.code_submitted, 
        grade=details.final_grade
    )
    
    return analysis

from src.application.teacher.queries.get_activity_students import GetActivityStudentsProgress, StudentActivityProgressDTO

@router.get("/activities/{activity_id}/students", response_model=List[StudentActivityProgressDTO])
def get_activity_students_progress(
    activity_id: str,
    db: Session = Depends(get_db)
):
    query = GetActivityStudentsProgress(db)
    return query.execute(activity_id)

