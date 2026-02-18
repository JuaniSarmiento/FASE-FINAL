from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.infrastructure.auth.jwt_token_provider import JwtTokenProvider
from src.infrastructure.http.dependencies.container import get_token_provider

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

def get_current_user_id(
    token: str = Depends(oauth2_scheme),
    token_provider: JwtTokenProvider = Depends(get_token_provider)
) -> str:
    try:
        payload = token_provider.verify_token(token)
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user_id
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )
