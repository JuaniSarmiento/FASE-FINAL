import subprocess
import sys
import tempfile
import os
from src.domain.grading.ports.code_executor import CodeExecutor
from src.domain.grading.value_objects.execution_result import ExecutionResult

class LocalCodeExecutor(CodeExecutor):
    def execute(self, code: str, language: str, test_cases: list) -> ExecutionResult:
        if language != "python":
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr="Only Python supported in Local Executor",
                error="Unsupported Language"
            )

        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as tmp:
            tmp_path = tmp.name
            tmp.write(code)
            
        try:
            # Execute
            # Timeout 5 seconds
            result = subprocess.run(
                [sys.executable, tmp_path],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            return ExecutionResult(
                exit_code=result.returncode,
                stdout=result.stdout,
                stderr=result.stderr,
                error=None
            )
        except subprocess.TimeoutExpired:
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr="Timeout",
                error="Execution Timed Out"
            )
        except Exception as e:
            return ExecutionResult(
                exit_code=1,
                stdout="",
                stderr=str(e),
                error=str(e)
            )
        finally:
            if os.path.exists(tmp_path):
                os.remove(tmp_path)
