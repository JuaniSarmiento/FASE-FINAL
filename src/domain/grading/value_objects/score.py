from dataclasses import dataclass
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class Score(ValueObject):
    value: float
    
    def __post_init__(self):
        if self.value < 0 or self.value > 100:
            raise ValueError("Score must be between 0 and 100")
            
    def __str__(self) -> str:
        return str(self.value)
