from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class CreateActivityRequest(BaseModel):
    title: str
    course_id: str
    description: Optional[str] = None
    type: str = "practice"

class ActivityResponse(BaseModel):
    id: str
    course_id: str
    teacher_id: str
    title: str
    description: Optional[str]
    type: str
    status: str
    order: int
    created_at: datetime
    updated_at: datetime
    exercise_count: int = 0
