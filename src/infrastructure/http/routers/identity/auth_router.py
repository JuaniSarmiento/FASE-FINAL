from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from src.application.identity.dtos.auth_dtos import RegisterUserRequest, AuthResponseDTO, LoginRequest
from src.application.identity.commands.register_user import RegisterUser
from src.application.identity.commands.authenticate_user import AuthenticateUser
from src.infrastructure.http.dependencies.container import get_register_use_case, get_authenticate_use_case

router = APIRouter()

@router.post("/register", response_model=AuthResponseDTO, status_code=status.HTTP_201_CREATED)
def register(
    request: RegisterUserRequest,
    use_case: RegisterUser = Depends(get_register_use_case)
):
    try:
        return use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/token", response_model=AuthResponseDTO)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    use_case: AuthenticateUser = Depends(get_authenticate_use_case)
):
    try:
        request = LoginRequest(email=form_data.username, password=form_data.password)
        return use_case.execute(request)
    except ValueError as e:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
