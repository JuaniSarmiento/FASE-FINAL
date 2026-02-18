import json
from typing import Optional, List
from sqlalchemy.orm import Session
from ....domain.learning.ports.exercise_repository import ExerciseRepository
from ....domain.learning.entities.exercise import Exercise
from ....domain.learning.entities.test_case import TestCase
from ....domain.learning.value_objects.difficulty import Difficulty
from ....domain.learning.value_objects.programming_language import ProgrammingLanguage
from ....domain.learning.value_objects.exercise_status import ExerciseStatus
from ..models.learning_models import ExerciseModel

class SqlAlchemyExerciseRepository(ExerciseRepository):
    def __init__(self, session: Session):
        self.session = session

    def save(self, exercise: Exercise) -> None:
        model = self.session.query(ExerciseModel).filter_by(id=exercise.id).first()
        if not model:
            model = ExerciseModel(id=exercise.id)
            self.session.add(model)
        
        model.activity_id = exercise.activity_id
        model.title = exercise.title
        model.problem_statement = exercise.problem_statement
        model.starter_code = exercise.starter_code
        model.solution_code = exercise.solution_code
        model.difficulty = exercise.difficulty.value
        model.language = exercise.language.value
        model.status = exercise.status.value
        
        # Serialize test cases
        test_cases_data = [
            {
                "input_data": tc.input_data,
                "expected_output": tc.expected_output,
                "is_hidden": tc.is_hidden,
                "weight": tc.weight
            } for tc in exercise.test_cases
        ]
        model.test_cases_json = json.dumps(test_cases_data)
        
        model.updated_at = exercise.updated_at

    def find_by_id(self, exercise_id: str) -> Optional[Exercise]:
        model = self.session.query(ExerciseModel).filter_by(id=exercise_id).first()
        if not model:
            return None
            
        return self._map_to_entity(model)

    def list_by_activity(self, activity_id: str) -> List[Exercise]:
        models = self.session.query(ExerciseModel).filter_by(activity_id=activity_id).all()
        return [self._map_to_entity(m) for m in models]

    def count_by_activity(self, activity_id: str) -> int:
        return self.session.query(ExerciseModel).filter_by(activity_id=activity_id).count()

    def _map_to_entity(self, model: ExerciseModel) -> Exercise:
        try:
            test_cases_data = json.loads(model.test_cases_json or "[]")
            test_cases = [
                TestCase(
                    input_data=tc["input_data"],
                    expected_output=tc["expected_output"],
                    is_hidden=tc.get("is_hidden", False),
                    weight=tc.get("weight", 1.0)
                ) for tc in test_cases_data
            ]
        except Exception as e:
            print(f"Error parsing test cases for exercise {model.id}: {e}")
            test_cases = []

        try:
            diff = Difficulty(model.difficulty)
        except ValueError:
            diff = Difficulty.MEDIUM # Fallback

        try:
            lang = ProgrammingLanguage(model.language)
        except ValueError:
            lang = ProgrammingLanguage.PYTHON # Fallback
            
        try:
            status = ExerciseStatus(model.status)
        except ValueError:
            status = ExerciseStatus.DRAFT # Fallback
        
        return Exercise(
            id=model.id,
            activity_id=model.activity_id,
            title=model.title,
            problem_statement=model.problem_statement,
            starter_code=model.starter_code,
            solution_code=model.solution_code,
            difficulty=diff,
            language=lang,
            status=status,
            test_cases=test_cases,
            created_at=model.created_at,
            updated_at=model.updated_at
        )
