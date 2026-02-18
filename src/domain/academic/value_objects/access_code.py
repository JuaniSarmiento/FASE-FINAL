from dataclasses import dataclass
import random
import string
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class AccessCode(ValueObject):
    code: str
    
    def __post_init__(self):
        if not self.code:
             raise ValueError("Access code cannot be empty")
        if len(self.code) < 6:
             raise ValueError("Access code too short")
            
    def __str__(self) -> str:
        return self.code
        
    @staticmethod
    def generate(length: int = 8) -> 'AccessCode':
        chars = string.ascii_uppercase + string.digits
        code = ''.join(random.choice(chars) for _ in range(length))
        return AccessCode(code)
