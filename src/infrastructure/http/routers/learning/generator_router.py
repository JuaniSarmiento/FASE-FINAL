from fastapi import APIRouter, Depends, HTTPException
from typing import List
from src.application.learning.dtos.generate_exercises_dto import GenerateExercisesRequest, GeneratedExerciseDTO
from src.application.learning.commands.generate_exercises import GenerateExercises
from src.domain.learning.exceptions import ActivityNotFoundException
from src.infrastructure.http.dependencies.container import get_generate_exercises_use_case

router = APIRouter()

@router.post("/generate", response_model=List[GeneratedExerciseDTO])
def generate_exercises(
    request: GenerateExercisesRequest,
    use_case: GenerateExercises = Depends(get_generate_exercises_use_case)
):
    try:
        return use_case.execute(request)
    except ActivityNotFoundException as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
