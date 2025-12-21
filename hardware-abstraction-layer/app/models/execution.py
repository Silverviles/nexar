from typing import Any, Dict, List, Optional
from enum import Enum
from pydantic import BaseModel, Field


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


class JobSubmission(BaseModel):
    id: str
    request: JobRequest
    status: str = "PENDING"
    created_at: float
    provider_job_id: Optional[str] = None
