from abc import ABC, abstractmethod
from ..value_objects.execution_result import ExecutionResult

class CodeExecutor(ABC):
    @abstractmethod
    def execute(self, code: str, language: str, test_cases: list) -> ExecutionResult:
        """Execute code in a sandbox."""
        pass
