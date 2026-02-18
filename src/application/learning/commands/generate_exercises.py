from typing import List
from src.application.shared.unit_of_work import UnitOfWork
from src.domain.learning.ports.exercise_repository import ExerciseRepository
from src.domain.learning.ports.document_repository import DocumentRepository
from src.domain.learning.ports.activity_repository import ActivityRepository
from src.domain.learning.value_objects.difficulty import Difficulty
from src.domain.learning.value_objects.programming_language import ProgrammingLanguage
from src.domain.learning.exceptions import ActivityNotFoundException
from src.application.learning.ports.exercise_generator import IExerciseGenerator
from src.application.learning.dtos.generate_exercises_dto import GenerateExercisesRequest, GeneratedExerciseDTO

class GenerateExercises:
    def __init__(
        self, 
        exercise_generator: IExerciseGenerator,
        exercise_repository: ExerciseRepository,
        activity_repository: ActivityRepository,
        document_repository: DocumentRepository,
        unit_of_work: UnitOfWork
    ):
        self.exercise_generator = exercise_generator
        self.exercise_repository = exercise_repository
        self.activity_repository = activity_repository
        self.document_repository = document_repository
        self.unit_of_work = unit_of_work
        
    def execute(self, request: GenerateExercisesRequest) -> List[GeneratedExerciseDTO]:
        # 1. Validate activity exists
        activity = self.activity_repository.find_by_id(request.activity_id)
        if not activity:
            raise ActivityNotFoundException(f"Activity {request.activity_id} not found")
            
        # 2. Convert DTO strings to Domain VOs
        try:
            # Normalize inputs
            difficulty_str = request.difficulty.title() if request.difficulty else "Medium"
            language_str = request.language.lower() if request.language else "python"
            
            difficulty_vo = Difficulty(difficulty_str)
            language_vo = ProgrammingLanguage(language_str)
        except ValueError as e:
            raise ValueError(f"Invalid difficulty or language: {e}")
            
        # 2b. Retrieve Context from Documents (RAG Lite)
        context = ""
        if request.activity_id:
            documents = self.document_repository.find_by_activity(request.activity_id)
            if documents:
                # Concatenate text from documents
                context = "\n\n".join([f"Document: {d.filename}\n{d.content_text or ''}" for d in documents])
        
        # 3. Call AI Port to generate exercises
        generated_exercises = self.exercise_generator.generate(
            topic=request.topic,
            count=request.count,
            difficulty=difficulty_vo,
            language=language_vo,
            context=context if context else None
        )
        
        # 4. Save generated exercises and map to DTOs
        result_dtos = []
        
        # Start transaction
        with self.unit_of_work:
            for exercise in generated_exercises:
                # Link exercise to activity
                exercise.activity_id = activity.id
                
                self.exercise_repository.save(exercise)
                
                result_dtos.append(GeneratedExerciseDTO(
                    id=exercise.id,
                    title=exercise.title,
                    problem_statement=exercise.problem_statement,
                    difficulty=exercise.difficulty.value,
                    language=exercise.language.value
                ))
            
            self.unit_of_work.commit()
            
        return result_dtos
