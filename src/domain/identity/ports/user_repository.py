from abc import ABC, abstractmethod
from typing import Optional
from ..entities.user import User
from ..value_objects.email import Email
from ..value_objects.user_id import UserId

class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        """Save a user."""
        pass
    
    @abstractmethod
    def find_by_id(self, user_id: UserId) -> Optional[User]:
        """Find a user by ID."""
        pass
    
    @abstractmethod
    def find_by_email(self, email: Email) -> Optional[User]:
        """Find a user by email."""
        pass
    
    @abstractmethod
    def delete(self, user_id: UserId) -> None:
        """Delete a user."""
        pass

    @abstractmethod
    def find_all_by_role(self, role_name: str) -> list[User]:
        pass
