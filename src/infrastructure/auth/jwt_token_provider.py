from datetime import datetime, timedelta
from typing import Dict, Any
from jose import jwt, JWTError
from src.domain.identity.ports.token_provider import ITokenProvider
from src.infrastructure.config.settings import settings

class JwtTokenProvider(ITokenProvider):
    def __init__(self, secret_key: str = settings.SECRET_KEY, algorithm: str = "HS256"):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_token_expire_minutes = 30
        self.refresh_token_expire_minutes = 60 * 24 * 7 # 7 days

    def create_access_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.access_token_expire_minutes)
        to_encode.update({"type": "access", "exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.refresh_token_expire_minutes)
        to_encode.update({"type": "refresh", "exp": expire})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    def verify_token(self, token: str) -> Dict[str, Any]:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except JWTError:
            raise ValueError("Invalid token")
