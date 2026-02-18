from pydantic import BaseModel
from typing import List

class StudentDTO(BaseModel):
    user_id: str
    full_name: str
    email: str
    role: str = "student"
    status: str = "active"

class AddStudentsRequest(BaseModel):
    student_ids: List[str]
