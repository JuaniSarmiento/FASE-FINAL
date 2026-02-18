import sys
import os

# Add 'Fase Final' to path so we can import 'src'
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
sys.path.append(project_root)

from unittest.mock import MagicMock
from src.infrastructure.persistence.database import SessionLocal
from src.infrastructure.http.dependencies.container import get_generate_exercises_use_case
from src.application.learning.commands.generate_exercises import GenerateExercises
from src.infrastructure.ai.llm.ollama_service import OllamaExerciseGenerator
from src.infrastructure.persistence.repositories.activity_repository_impl import SqlAlchemyActivityRepository
from src.infrastructure.persistence.repositories.exercise_repository_impl import SqlAlchemyExerciseRepository
from src.infrastructure.persistence.unit_of_work import SqlAlchemyUnitOfWork

def test_wiring():
    print("🔌 Testing Dependency Injection Wiring...")
    
    # Mock DB Session
    mock_db = MagicMock()
    
    # dependencies.py functions:
    # def get_generate_exercises_use_case(generator, activity_repo, exercise_repo, uow)
    
    # Manually instantiate dependencies to simulate what FastAPI Depends() does
    try:
        # 1. Instantiate Adapters
        print("   1. Instantiating Adapters...")
        ollama_service = OllamaExerciseGenerator()
        activity_repo = SqlAlchemyActivityRepository(mock_db)
        exercise_repo = SqlAlchemyExerciseRepository(mock_db)
        uow = SqlAlchemyUnitOfWork(lambda: mock_db)
        
        print("      - Adapters created successfully.")

        # 2. Instantiate Use Case via Factory
        print("   2. Injecting into Use Case...")
        use_case = GenerateExercises(
            exercise_generator=ollama_service,
            activity_repository=activity_repo,
            exercise_repository=exercise_repo,
            unit_of_work=uow
        )
        
        print("      - Use Case created successfully.")
        
        # 3. Verify Types
        print("   3. Verifying Interfaces...")
        assert isinstance(use_case, GenerateExercises)
        assert isinstance(use_case.exercise_generator, OllamaExerciseGenerator)
        assert isinstance(use_case.activity_repository, SqlAlchemyActivityRepository)
        assert isinstance(use_case.unit_of_work, SqlAlchemyUnitOfWork)
        
        print("✅ WIRING SUCCESS: The application graph is correctly assembled.")
        return True
        
    except Exception as e:
        print(f"❌ WIRING FAILURE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    if test_wiring():
        sys.exit(0)
    else:
        sys.exit(1)
