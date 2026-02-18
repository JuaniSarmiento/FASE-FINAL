from dataclasses import dataclass
from typing import Optional
from src.domain.shared.value_object import ValueObject

@dataclass(frozen=True)
class ExecutionResult(ValueObject):
    exit_code: int
    stdout: str
    stderr: str
    error: Optional[str] = None
    
    @property
    def is_success(self) -> bool:
        return self.exit_code == 0 and not self.error
