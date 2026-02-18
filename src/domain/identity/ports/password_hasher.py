from abc import ABC, abstractmethod
from ..value_objects.password import PasswordHash

class PasswordHasher(ABC):
    @abstractmethod
    def hash(self, password: str) -> PasswordHash:
        """Hash a plain text password."""
        pass
    
    @abstractmethod
    def verify(self, plain_password: str, hashed_password: PasswordHash) -> bool:
        """Verify a plain text password against a hash."""
        pass
