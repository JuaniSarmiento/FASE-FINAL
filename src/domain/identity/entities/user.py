from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Optional

from src.domain.shared.entity import AggregateRoot
from ..value_objects.user_id import UserId
from ..value_objects.email import Email
from ..value_objects.password import PasswordHash

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"
    ADMIN = "admin"

@dataclass(kw_only=True)
class User(AggregateRoot):
    email: Email
    hashed_password: PasswordHash
    full_name: Optional[str] = None
    roles: List[UserRole] = field(default_factory=list)
    is_active: bool = True
    is_verified: bool = False
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    
    # Override id to use strong UserId
    id: UserId = field(default_factory=UserId.next_id)

    @classmethod
    def create(cls, email: Email, password: PasswordHash, role: UserRole, full_name: Optional[str] = None) -> 'User':
        return cls(
            email=email,
            hashed_password=password,
            roles=[role],
            full_name=full_name
        )

    def add_role(self, role: UserRole) -> None:
        if role not in self.roles:
            self.roles.append(role)
            self.updated_at = datetime.now()

    def remove_role(self, role: UserRole) -> None:
        if role in self.roles:
            self.roles.remove(role)
            self.updated_at = datetime.now()
            
    def verify(self) -> None:
        self.is_verified = True
        self.updated_at = datetime.now()
        
    def activate(self) -> None:
        self.is_active = True
        self.updated_at = datetime.now()
        
    def deactivate(self) -> None:
        self.is_active = False
        self.updated_at = datetime.now()
