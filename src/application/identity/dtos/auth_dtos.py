from dataclasses import dataclass
from typing import Optional, List
from src.application.shared.dtos.common import DTO

@dataclass
class RegisterUserRequest(DTO):
    email: str
    password: str
    role: str = "student"
    full_name: Optional[str] = None

@dataclass
class LoginRequest(DTO):
    email: str
    password: str

@dataclass
class TokenDTO(DTO):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

@dataclass
class UserDTO(DTO):
    id: str
    email: str
    role: str
    full_name: Optional[str]
    is_active: bool

@dataclass
class AuthResponseDTO(DTO):
    user: UserDTO
    tokens: TokenDTO
