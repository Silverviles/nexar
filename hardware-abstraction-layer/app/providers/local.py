import io
import sys
import traceback
import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class LocalClassicalProvider(ClassicalProvider):
    """
    A classical provider that executes code locally.
    WARNING: This is for development/prototyping only. Executing arbitrary code is a security risk.
    """

    def __init__(self):
        self._jobs: Dict[str, Dict[str, Any]] = {}

    def get_provider_name(self) -> str:
        return "local"

    def list_devices(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "local_python",
                "type": "cpu",
                "description": "Local Python execution environment",
                "status": "active"
            }
        ]

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "status": "RUNNING",
            "result": None
        }

        # Execute immediately for this prototype
        try:
            # Capture stdout/stderr
            old_stdout = sys.stdout
            old_stderr = sys.stderr
            redirected_output = io.StringIO()
            redirected_error = io.StringIO()
            sys.stdout = redirected_output
            sys.stderr = redirected_error

            # Prepare execution environment
            local_scope = {}

            # Execute the code
            # We assume the code might define functions or just run scripts.
            # If entry_point is provided, we'd call it.
            # For now, just exec the block.
            exec(task.code, {}, local_scope)

            # Restore stdout/stderr
            sys.stdout = old_stdout
            sys.stderr = old_stderr

            output = redirected_output.getvalue()
            error = redirected_error.getvalue()

            self._jobs[job_id]["status"] = "COMPLETED"
            self._jobs[job_id]["result"] = {
                "stdout": output,
                "stderr": error,
                "variables": {k: str(v) for k, v in local_scope.items() if not k.startswith('__')}
            }

        except Exception as e:
            # Restore stdout/stderr if they weren't restored
            sys.stdout = sys.__stdout__
            sys.stderr = sys.__stderr__

            self._jobs[job_id]["status"] = "FAILED"
            self._jobs[job_id]["result"] = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }

        return job_id

    def get_job_status(self, job_id: str) -> str:
        return self._jobs.get(job_id, {}).get("status", "UNKNOWN")

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return self._jobs.get(job_id, {}).get("result", {})
