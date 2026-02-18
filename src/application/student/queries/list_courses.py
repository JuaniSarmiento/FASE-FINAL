import logging
from dataclasses import dataclass
from typing import List, Optional, Dict
from src.application.shared.dtos.common import DTO
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.academic.ports.enrollment_repository import EnrollmentRepository

logger = logging.getLogger(__name__)

@dataclass
class ActivitySummaryDTO(DTO):
    activity_id: str
    title: str
    description: str
    difficulty: str
    status: str

@dataclass
class ModuleSummaryDTO(DTO):
    module_id: str
    title: str
    activity_count: int
    activities: List[ActivitySummaryDTO]

@dataclass
class CourseSummaryDTO(DTO):
    course_id: str
    name: str
    year: int
    semester: str
    modules: List[ModuleSummaryDTO]

class ListStudentCourses:
    def __init__(self, activity_repository: ActivityRepository, enrollment_repository: EnrollmentRepository):
        self.activity_repository = activity_repository
        self.enrollment_repository = enrollment_repository

    def execute(self, student_id: str) -> List[CourseSummaryDTO]:
        """
        List all courses/modules for a student based on Enrollments.
        Only returns modules the student is actively enrolled in.
        """
        logger.info(f"Listing courses for student: {student_id}")
        
        # 1. Get enrollments for the student
        enrollments = self.enrollment_repository.list_by_student(student_id)
        enrolled_module_ids = {e.module_id for e in enrollments if e.module_id}
        
        logger.info(f"Found {len(enrollments)} enrollments, modules: {enrolled_module_ids}")

        if not enrolled_module_ids:
            return []

        # 2. Get all published modules and filter by enrollment
        all_activities = self.activity_repository.find_all_published()
        modules = [
            a for a in all_activities 
            if a.type.value == "module" and a.id in enrolled_module_ids
        ]
        
        # Group by "Parent Course"
        courses_map: Dict[str, CourseSummaryDTO] = {}
        
        for module in modules:
            course_id = module.course_id
            
            if course_id not in courses_map:
                # Placeholder Course logic
                courses_map[course_id] = CourseSummaryDTO(
                    course_id=course_id,
                    name="Curso General" if course_id == "default_course" else "Curso",
                    year=2026,
                    semester="1",
                    modules=[]
                )
            
            # Get activities for the module
            activities_in_module = self.activity_repository.list_by_course(module.id)
            
            # Filter published and map to DTO
            published_activities = [a for a in activities_in_module if a.status.value == "published"]
            
            activity_dtos = [
                ActivitySummaryDTO(
                    activity_id=a.id,
                    title=a.title,
                    description=a.description,
                    difficulty="intermediate", # Default or extract from description/metadata keys
                    status=a.status.value
                )
                for a in published_activities
            ]

            courses_map[course_id].modules.append(ModuleSummaryDTO(
                module_id=module.id,
                title=module.title,
                activity_count=len(activity_dtos),
                activities=activity_dtos
            ))
        
        return list(courses_map.values())
