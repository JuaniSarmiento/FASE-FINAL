from dataclasses import dataclass
import uuid
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class UserId(ValueObject):
    value: str
    
    def __post_init__(self):
        try:
            uuid.UUID(self.value)
        except ValueError:
            raise ValueError(f"Invalid UUID for UserId: {self.value}")

    def __str__(self) -> str:
        return self.value
        
    @staticmethod
    def next_id() -> 'UserId':
        return UserId(str(uuid.uuid4()))
