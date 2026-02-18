from dataclasses import dataclass
import re
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class Email(ValueObject):
    address: str
    
    # Simple email regex
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    def __post_init__(self):
        if not self.address:
            raise ValueError("Email address cannot be empty")
        
        if not self.EMAIL_PATTERN.match(self.address):
            raise ValueError(f"Invalid email address: {self.address}")
            
    def __str__(self) -> str:
        return self.address
