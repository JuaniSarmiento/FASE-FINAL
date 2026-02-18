from dataclasses import dataclass
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class PasswordHash(ValueObject):
    value: str
    
    def __post_init__(self):
        if not self.value:
            raise ValueError("Password hash cannot be empty")
            
    def __str__(self) -> str:
        return self.value
