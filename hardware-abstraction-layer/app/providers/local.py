import io
import json
import os
import subprocess
import sys
import tempfile
import traceback
import uuid
from typing import List, Dict, Any

from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class LocalClassicalProvider(ClassicalProvider):
    """
    A classical provider that executes code locally via subprocess.

    Runs user code in an isolated Python subprocess using the HAL venv,
    so all installed packages (qiskit, numpy, scipy, etc.) are available.

    WARNING: This is for development/prototyping only.
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

    def _get_venv_python(self) -> str:
        """Get the path to the venv's Python interpreter."""
        # We're running inside the HAL venv, so sys.executable is already correct
        return sys.executable

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "status": "RUNNING",
            "result": None
        }

        try:
            result = self._run_code_subprocess(task.code)
            self._jobs[job_id]["status"] = "COMPLETED"
            self._jobs[job_id]["result"] = result
        except Exception as e:
            self._jobs[job_id]["status"] = "FAILED"
            self._jobs[job_id]["result"] = {
                "error": str(e),
                "traceback": traceback.format_exc()
            }

        return job_id

    def _run_code_subprocess(self, code: str) -> Dict[str, Any]:
        """
        Execute user code in an isolated subprocess.

        This approach:
        - Uses the HAL venv Python so all installed packages are available
        - Isolates user code from the server process (crashes don't kill HAL)
        - Captures stdout, stderr, and serializable variables from the user scope
        - Has a timeout to prevent infinite loops
        """
        # Write the user code into a temp file wrapped in a harness that
        # captures the user's defined variables and prints them as JSON.
        wrapper = _build_wrapper(code)

        tmp_file = None
        try:
            tmp_file = tempfile.NamedTemporaryFile(
                mode="w",
                suffix=".py",
                delete=False,
                encoding="utf-8",
            )
            tmp_file.write(wrapper)
            tmp_file.close()

            python = self._get_venv_python()
            env = os.environ.copy()
            env["PYTHONUTF8"] = "1"
            # Ensure matplotlib doesn't try to open GUI windows
            env["MPLBACKEND"] = "Agg"

            proc = subprocess.run(
                [python, tmp_file.name],
                capture_output=True,
                text=True,
                timeout=120,  # 2 minute timeout
                env=env,
            )

            stdout = proc.stdout
            stderr = proc.stderr

            # The wrapper prints a JSON sentinel line at the end of stdout
            # with the user-defined variables. Extract it.
            variables = {}
            sentinel = "@@NEXAR_VARS@@"
            if sentinel in stdout:
                parts = stdout.split(sentinel)
                stdout = parts[0]  # Everything before the sentinel is real stdout
                try:
                    variables = json.loads(parts[1].strip())
                except (json.JSONDecodeError, IndexError):
                    pass

            if proc.returncode != 0:
                raise RuntimeError(
                    stderr.strip() or f"Process exited with code {proc.returncode}"
                )

            return {
                "stdout": stdout,
                "stderr": stderr,
                "variables": variables,
            }

        except subprocess.TimeoutExpired:
            raise RuntimeError("Code execution timed out after 120 seconds")
        finally:
            if tmp_file and os.path.exists(tmp_file.name):
                os.unlink(tmp_file.name)

    def get_job_status(self, job_id: str) -> str:
        return self._jobs.get(job_id, {}).get("status", "UNKNOWN")

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        return self._jobs.get(job_id, {}).get("result", {})


def _build_wrapper(user_code: str) -> str:
    """
    Wraps user code in a harness that:
    1. Executes the user code with full builtins/imports available
    2. Captures user-defined variables and prints them as JSON
    """
    # Escape the user code for embedding in a triple-quoted string
    escaped = user_code.replace("\\", "\\\\").replace('"""', '\\"\\"\\"')

    return f'''
import json
import sys

# ── Execute user code ──
_user_scope = {{}}
try:
    exec("""{escaped}""", _user_scope)
except SystemExit:
    pass

# ── Extract serializable variables ──
_vars = {{}}
for _k, _v in _user_scope.items():
    if _k.startswith("_"):
        continue
    try:
        json.dumps(_v)
        _vars[_k] = _v
    except (TypeError, ValueError, OverflowError):
        _vars[_k] = repr(_v)

print("@@NEXAR_VARS@@")
print(json.dumps(_vars, default=str))
'''
