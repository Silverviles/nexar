import time
import asyncio
import threading
from typing import Dict, List, Optional
from collections import defaultdict
import uuid

from typing import Dict, List, Optional, Any

from app.core.config import settings
from app.messaging.factory import messaging_client
from app.models.execution import JobRequest, JobSubmission, JobPriority, OptimizationStrategy
from app.services.factory import compute_service
from app.providers.base import BaseProvider

# Configuration
BATCH_CHECK_INTERVAL = 2.0  # Seconds to check for batches
COST_STRATEGY_WAIT_TIME = 10.0  # Max wait time for COST strategy
TIME_STRATEGY_WAIT_TIME = 1.0   # Max wait time for TIME strategy
MAX_BATCH_SIZE = 10  # Default max batch size

class JobManager:
    def __init__(self):
        self._pending_jobs: Dict[str, List[JobSubmission]] = defaultdict(list)
        self._jobs: Dict[str, JobSubmission] = {}
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread = None

    def start(self):
        if not self._running:
            self._running = True
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()

    def _publish_status_update(self, submission: JobSubmission, status: str, extra_data: Dict = None):
        if messaging_client:
            message = {
                "job_id": submission.id,
                "provider_job_id": submission.provider_job_id,
                "status": status,
                "provider": submission.request.provider_name,
                "device": submission.request.device_name,
                "timestamp": time.time()
            }
            if extra_data:
                message.update(extra_data)
            
            messaging_client.publish_message(settings.PUBSUB_TOPIC_NAME, message)

    def submit_job(self, request: JobRequest) -> str:
        job_id = str(uuid.uuid4())
        submission = JobSubmission(
            id=job_id,
            request=request,
            created_at=time.time()
        )
        
        with self._lock:
            self._jobs[job_id] = submission
            
            # If HIGH priority, execute immediately
            if request.priority == JobPriority.HIGH:
                submission.status = "QUEUED"
                self._publish_status_update(submission, "QUEUED")
                self._execute_batch([submission])
            else:
                # Add to pending queue (keyed by provider + device)
                key = f"{request.provider_name}|{request.device_name}"
                self._pending_jobs[key].append(submission)
                submission.status = "QUEUED"
                self._publish_status_update(submission, "QUEUED")
        
        return job_id

    def get_job_status(self, job_id: str) -> str:
        # Check internal mapping first
        if job_id in self._jobs:
            submission = self._jobs[job_id]
            if submission.provider_job_id:
                # Delegate to provider
                status = compute_service.get_job_status(
                    submission.request.provider_name, 
                    submission.provider_job_id
                )
                if status != submission.status:
                    submission.status = status
                    self._publish_status_update(submission, status)
                return status
            return submission.status
        return "UNKNOWN"

    def get_job_result(self, job_id: str) -> Dict:
        if job_id in self._jobs:
            submission = self._jobs[job_id]
            if submission.provider_job_id:
                result = compute_service.get_job_result(
                    submission.request.provider_name,
                    submission.provider_job_id
                )
                # Assuming the job is complete if we get a result
                submission.status = "COMPLETED"
                self._publish_status_update(submission, "COMPLETED", extra_data={"result": result})
                return result
        return {}

    def _monitor_loop(self):
        while self._running:
            time.sleep(BATCH_CHECK_INTERVAL)
            with self._lock:
                self._process_queues()

    def _process_queues(self):
        current_time = time.time()
        for key, submissions in list(self._pending_jobs.items()):
            if not submissions:
                continue

            # All jobs in this queue share provider and device
            first_job = submissions[0]
            strategy = first_job.request.strategy
            
            # Determine threshold
            wait_limit = COST_STRATEGY_WAIT_TIME if strategy == OptimizationStrategy.COST else TIME_STRATEGY_WAIT_TIME
            batch_ready = False
            
            # Criteria 1: Max batch size reached
            if len(submissions) >= MAX_BATCH_SIZE:
                batch_ready = True
            
            # Criteria 2: Timeout reached for the OLDEST job
            elif (current_time - first_job.created_at) >= wait_limit:
                batch_ready = True
            
            if batch_ready:
                # Take up to MAX_BATCH_SIZE jobs
                batch = submissions[:MAX_BATCH_SIZE]
                self._pending_jobs[key] = submissions[MAX_BATCH_SIZE:]
                self._execute_batch(batch)

    def _execute_batch(self, batch: List[JobSubmission]):
        if not batch:
            return

        provider_name = batch[0].request.provider_name
        device_name = batch[0].request.device_name
        
        # Prepare tasks
        tasks = [sub.request.task for sub in batch]
        
        try:
            provider_job_ids = compute_service.execute_batch(
                provider_name, 
                tasks, 
                device_name, 
                shots=batch[0].request.shots # Assuming mostly same shots or taking first
            )
            
            # Update submissions
            for sub, p_id in zip(batch, provider_job_ids):
                sub.status = "SUBMITTED"
                sub.provider_job_id = p_id
                self._publish_status_update(sub, "SUBMITTED")
                
        except Exception as e:
            print(f"Batch execution failed: {e}")
            for sub in batch:
                sub.status = "FAILED"
                self._publish_status_update(sub, "FAILED", extra_data={"error": str(e)})

job_manager = JobManager()
# Start the background thread
job_manager.start()
