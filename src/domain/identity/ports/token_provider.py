from abc import ABC, abstractmethod
from typing import Dict, Any

class ITokenProvider(ABC):
    @abstractmethod
    def create_access_token(self, data: Dict[str, Any]) -> str:
        """Create a new access token."""
        pass
    
    @abstractmethod
    def create_refresh_token(self, data: Dict[str, Any]) -> str:
        """Create a new refresh token."""
        pass
    
    @abstractmethod
    def verify_token(self, token: str) -> Dict[str, Any]:
        """Verify and decode a token."""
        pass
