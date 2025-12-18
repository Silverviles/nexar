from typing import Dict, Any, Optional

from pydantic import BaseModel


class ClassicalTask(BaseModel):
    """
    A Pydantic model for a classical compute task.
    """
    code: str
    language: str = "python"
    entry_point: Optional[str] = None  # For functions, if we support that later
    parameters: Dict[str, Any] = {}


class ClassicalJob(BaseModel):
    """
    A Pydantic model for a classical job.
    """
    job_id: str
    provider: str
    status: str


class ClassicalResult(BaseModel):
    """
    A Pydantic model for a classical job result.
    """
    job_id: str
    provider: str
    result: Dict[str, Any]  # e.g. {"stdout": "...", "stderr": "...", "return_value": ...}
