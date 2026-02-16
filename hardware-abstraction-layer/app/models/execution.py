from typing import Any, Optional
from enum import Enum
from datetime import datetime
from pydantic import BaseModel, Field, computed_field


class JobPriority(str, Enum):
    HIGH = "high"
    STANDARD = "standard"


class OptimizationStrategy(str, Enum):
    TIME = "time"  # Execute as soon as possible (smaller batches)
    COST = "cost"  # Maximize batch size (wait longer)


class JobRequest(BaseModel):
    task: Any
    provider_name: str
    device_name: str
    shots: int = 1024
    priority: JobPriority = JobPriority.HIGH
    strategy: OptimizationStrategy = OptimizationStrategy.TIME
    user_id: Optional[str] = None


class ScheduledJobRequest(JobRequest):
    """Job request with optional scheduled execution time."""
    scheduled_time: Optional[datetime] = None
    queue_if_unavailable: bool = False


class PythonCodeRequest(BaseModel):
    """Request model for submitting raw Python code to IBM Quantum."""
    code: str = Field(..., description="Python code to execute (must define a 'circuit' variable)")
    device_name: str = Field(..., description="IBM Quantum device name")
    shots: int = Field(default=1024, ge=1, le=100000)
    queue_if_unavailable: bool = Field(default=False, description="Queue job if device is unavailable")
    scheduled_time: Optional[datetime] = Field(default=None, description="Schedule job for future execution")


class DeviceAvailability(BaseModel):
    """Model representing device availability status."""
    device_name: str
    is_operational: bool
    pending_jobs: int
    queue_threshold: int

    @computed_field
    @property
    def is_available(self) -> bool:
        """Device is available if operational and pending jobs below threshold."""
        return self.is_operational and self.pending_jobs < self.queue_threshold


class JobSubmission(BaseModel):
    id: str
    request: JobRequest
    status: str = "PENDING"
    created_at: float
    provider_job_id: Optional[str] = None
    scheduled_time: Optional[float] = None  # Unix timestamp for scheduled execution
    is_python_code: bool = False  # Flag for Python code jobs
