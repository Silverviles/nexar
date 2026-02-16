import time
import threading
import json
import logging
from typing import Dict, List, Optional, Any
from collections import defaultdict
import uuid
from datetime import datetime

from app.core.config import settings
from app.messaging.factory import messaging_client
from app.models.execution import (
    JobRequest, JobSubmission, JobPriority, OptimizationStrategy
)
from app.services.factory import compute_service

logger = logging.getLogger(__name__)

# Configuration
BATCH_CHECK_INTERVAL = 2.0  # Seconds to check for batches
COST_STRATEGY_WAIT_TIME = 10.0  # Max wait time for COST strategy
TIME_STRATEGY_WAIT_TIME = 1.0   # Max wait time for TIME strategy
MAX_BATCH_SIZE = 10  # Default max batch size
SCHEDULER_CHECK_INTERVAL = 1.0  # Seconds to check scheduled jobs

# Redis keys
REDIS_JOBS_KEY = "hal:jobs"
REDIS_SCHEDULED_KEY = "hal:scheduled_jobs"
REDIS_PENDING_KEY = "hal:pending_jobs"


class RedisClient:
    """Simple Redis client wrapper with graceful fallback to in-memory storage."""

    def __init__(self):
        self._redis = None
        self._in_memory_fallback = {}
        self._initialize()

    def _initialize(self):
        if settings.REDIS_URL:
            try:
                import redis
                self._redis = redis.from_url(settings.REDIS_URL, decode_responses=True)
                # Test connection
                self._redis.ping()
                logger.info(f"Redis connected: {settings.REDIS_URL}")
            except ImportError:
                logger.warning("redis package not installed. Using in-memory storage.")
                self._redis = None
            except Exception as e:
                logger.warning(f"Redis connection failed: {e}. Using in-memory storage.")
                self._redis = None
        else:
            logger.info("REDIS_URL not configured. Using in-memory storage for jobs.")

    @property
    def is_connected(self) -> bool:
        return self._redis is not None

    def hset(self, name: str, key: str, value: str):
        if self._redis:
            self._redis.hset(name, key, value)
        else:
            if name not in self._in_memory_fallback:
                self._in_memory_fallback[name] = {}
            self._in_memory_fallback[name][key] = value

    def hget(self, name: str, key: str) -> Optional[str]:
        if self._redis:
            return self._redis.hget(name, key)
        return self._in_memory_fallback.get(name, {}).get(key)

    def hgetall(self, name: str) -> Dict[str, str]:
        if self._redis:
            return self._redis.hgetall(name)
        return self._in_memory_fallback.get(name, {})

    def hdel(self, name: str, key: str):
        if self._redis:
            self._redis.hdel(name, key)
        elif name in self._in_memory_fallback:
            self._in_memory_fallback[name].pop(key, None)

    def zadd(self, name: str, mapping: Dict[str, float]):
        """Add to sorted set with score (for scheduled jobs)."""
        if self._redis:
            self._redis.zadd(name, mapping)
        else:
            if name not in self._in_memory_fallback:
                self._in_memory_fallback[name] = {}
            self._in_memory_fallback[name].update(mapping)

    def zrangebyscore(self, name: str, min_score: float, max_score: float) -> List[str]:
        """Get items from sorted set by score range."""
        if self._redis:
            return self._redis.zrangebyscore(name, min_score, max_score)
        else:
            items = self._in_memory_fallback.get(name, {})
            return [k for k, v in items.items() if min_score <= v <= max_score]

    def zrem(self, name: str, *keys):
        """Remove items from sorted set."""
        if self._redis:
            self._redis.zrem(name, *keys)
        elif name in self._in_memory_fallback:
            for key in keys:
                self._in_memory_fallback[name].pop(key, None)


class JobManager:
    def __init__(self):
        self._pending_jobs: Dict[str, List[JobSubmission]] = defaultdict(list)
        self._jobs: Dict[str, JobSubmission] = {}
        self._scheduled_jobs: Dict[str, JobSubmission] = {}
        self._lock = threading.Lock()
        self._running = False
        self._monitor_thread = None
        self._scheduler_thread = None
        self._redis: Optional[RedisClient] = None

    def start(self):
        if not self._running:
            self._running = True

            # Initialize Redis client
            self._redis = RedisClient()

            # Load persisted jobs
            self._load_jobs_from_redis()

            # Start monitor thread for batch processing
            self._monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
            self._monitor_thread.start()

            # Start scheduler thread for scheduled jobs
            self._scheduler_thread = threading.Thread(target=self._scheduler_loop, daemon=True)
            self._scheduler_thread.start()

            logger.info("JobManager started with batch monitor and scheduler threads")

    def _load_jobs_from_redis(self):
        """Load persisted jobs from Redis on startup."""
        if not self._redis:
            return

        try:
            # Load regular jobs
            jobs_data = self._redis.hgetall(REDIS_JOBS_KEY)
            for job_id, job_json in jobs_data.items():
                try:
                    job_dict = json.loads(job_json)
                    submission = JobSubmission(**job_dict)
                    self._jobs[job_id] = submission
                except Exception as e:
                    logger.error(f"Failed to load job {job_id}: {e}")

            # Load scheduled jobs
            scheduled_data = self._redis.hgetall(REDIS_SCHEDULED_KEY)
            for job_id, job_json in scheduled_data.items():
                try:
                    job_dict = json.loads(job_json)
                    submission = JobSubmission(**job_dict)
                    self._scheduled_jobs[job_id] = submission
                except Exception as e:
                    logger.error(f"Failed to load scheduled job {job_id}: {e}")

            logger.info(f"Loaded {len(self._jobs)} jobs and {len(self._scheduled_jobs)} scheduled jobs from Redis")
        except Exception as e:
            logger.error(f"Failed to load jobs from Redis: {e}")

    def _persist_job(self, submission: JobSubmission):
        """Persist job to Redis."""
        if not self._redis:
            return

        try:
            job_json = submission.model_dump_json()
            self._redis.hset(REDIS_JOBS_KEY, submission.id, job_json)
        except Exception as e:
            logger.error(f"Failed to persist job {submission.id}: {e}")

    def _persist_scheduled_job(self, submission: JobSubmission):
        """Persist scheduled job to Redis with score = scheduled_time."""
        if not self._redis:
            return

        try:
            job_json = submission.model_dump_json()
            self._redis.hset(REDIS_SCHEDULED_KEY, submission.id, job_json)
            # Also add to sorted set for efficient time-based queries
            if submission.scheduled_time:
                self._redis.zadd(f"{REDIS_SCHEDULED_KEY}:by_time", {submission.id: submission.scheduled_time})
        except Exception as e:
            logger.error(f"Failed to persist scheduled job {submission.id}: {e}")

    def _remove_scheduled_job(self, job_id: str):
        """Remove scheduled job from Redis."""
        if not self._redis:
            return

        try:
            self._redis.hdel(REDIS_SCHEDULED_KEY, job_id)
            self._redis.zrem(f"{REDIS_SCHEDULED_KEY}:by_time", job_id)
        except Exception as e:
            logger.error(f"Failed to remove scheduled job {job_id}: {e}")

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
            if submission.scheduled_time:
                message["scheduled_time"] = submission.scheduled_time
            if extra_data:
                message.update(extra_data)
            
            messaging_client.publish_message(settings.PUBSUB_TOPIC_NAME, message)

    def submit_job(self, request: JobRequest, scheduled_time: Optional[datetime] = None,
                   queue_if_unavailable: bool = False, is_python_code: bool = False) -> str:
        """
        Submit a job for execution.

        Args:
            request: The job request
            scheduled_time: Optional datetime for scheduled execution
            queue_if_unavailable: If True, queue job when device is unavailable
            is_python_code: If True, this job contains Python code (not QASM)

        Returns:
            job_id: The HAL job ID
        """
        job_id = str(uuid.uuid4())

        # Convert scheduled_time to Unix timestamp
        scheduled_timestamp = None
        if scheduled_time:
            scheduled_timestamp = scheduled_time.timestamp()

        submission = JobSubmission(
            id=job_id,
            request=request,
            created_at=time.time(),
            scheduled_time=scheduled_timestamp,
            is_python_code=is_python_code
        )
        
        with self._lock:
            self._jobs[job_id] = submission
            self._persist_job(submission)

            # Handle scheduled jobs
            if scheduled_timestamp and scheduled_timestamp > time.time():
                submission.status = "SCHEDULED"
                self._scheduled_jobs[job_id] = submission
                self._persist_scheduled_job(submission)
                self._publish_status_update(submission, "SCHEDULED", {
                    "scheduled_for": datetime.fromtimestamp(scheduled_timestamp).isoformat()
                })
                logger.info(f"Job {job_id} scheduled for {datetime.fromtimestamp(scheduled_timestamp)}")
                return job_id

            # Check device availability if requested
            if queue_if_unavailable:
                availability = compute_service.check_device_availability(
                    request.provider_name,
                    request.device_name
                )
                if not availability.is_available:
                    # Queue the job for later
                    submission.status = "QUEUED_UNAVAILABLE"
                    key = f"{request.provider_name}|{request.device_name}"
                    self._pending_jobs[key].append(submission)
                    self._persist_job(submission)
                    self._publish_status_update(submission, "QUEUED_UNAVAILABLE", {
                        "reason": f"Device has {availability.pending_jobs} pending jobs (threshold: {availability.queue_threshold})",
                        "is_operational": availability.is_operational
                    })
                    logger.info(f"Job {job_id} queued - device {request.device_name} unavailable")
                    return job_id

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

    def submit_python_code_job(self, code: str, device_name: str, shots: int = 1024,
                                scheduled_time: Optional[datetime] = None,
                                queue_if_unavailable: bool = False) -> str:
        """
        Submit a Python code job specifically for IBM Quantum.

        Args:
            code: Python code that defines a 'circuit' variable
            device_name: IBM Quantum backend name
            shots: Number of measurement shots
            scheduled_time: Optional datetime for scheduled execution
            queue_if_unavailable: Queue if device unavailable

        Returns:
            job_id: The HAL job ID
        """
        # Create a job request with code as the task
        request = JobRequest(
            task=code,  # Store code as task
            provider_name="ibm-quantum",
            device_name=device_name,
            shots=shots,
            priority=JobPriority.HIGH
        )

        return self.submit_job(
            request,
            scheduled_time=scheduled_time,
            queue_if_unavailable=queue_if_unavailable,
            is_python_code=True
        )

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
                    self._persist_job(submission)
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
                self._persist_job(submission)
                self._publish_status_update(submission, "COMPLETED", extra_data={"result": result})
                return result
        return {}

    def get_scheduled_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs."""
        with self._lock:
            return [
                {
                    "job_id": sub.id,
                    "device_name": sub.request.device_name,
                    "scheduled_time": datetime.fromtimestamp(sub.scheduled_time).isoformat() if sub.scheduled_time else None,
                    "status": sub.status,
                    "created_at": datetime.fromtimestamp(sub.created_at).isoformat()
                }
                for sub in self._scheduled_jobs.values()
            ]

    def cancel_scheduled_job(self, job_id: str) -> bool:
        """Cancel a scheduled job."""
        with self._lock:
            if job_id in self._scheduled_jobs:
                submission = self._scheduled_jobs.pop(job_id)
                submission.status = "CANCELLED"
                self._jobs[job_id] = submission
                self._persist_job(submission)
                self._remove_scheduled_job(job_id)
                self._publish_status_update(submission, "CANCELLED")
                return True
            return False

    def _monitor_loop(self):
        while self._running:
            time.sleep(BATCH_CHECK_INTERVAL)
            with self._lock:
                self._process_queues()

    def _scheduler_loop(self):
        """Background loop to process scheduled jobs."""
        while self._running:
            time.sleep(SCHEDULER_CHECK_INTERVAL)
            current_time = time.time()

            with self._lock:
                # Find jobs ready to execute
                ready_jobs = []
                for job_id, submission in list(self._scheduled_jobs.items()):
                    if submission.scheduled_time and submission.scheduled_time <= current_time:
                        ready_jobs.append((job_id, submission))

                # Execute ready jobs
                for job_id, submission in ready_jobs:
                    logger.info(f"Executing scheduled job {job_id}")
                    self._scheduled_jobs.pop(job_id)
                    self._remove_scheduled_job(job_id)

                    submission.status = "QUEUED"
                    self._publish_status_update(submission, "QUEUED", {"reason": "Scheduled time reached"})
                    self._execute_batch([submission])

    def _process_queues(self):
        current_time = time.time()
        for key, submissions in list(self._pending_jobs.items()):
            if not submissions:
                continue

            # Check if any jobs are waiting due to unavailable device
            unavailable_jobs = [s for s in submissions if s.status == "QUEUED_UNAVAILABLE"]
            if unavailable_jobs:
                # Check device availability
                first_job = unavailable_jobs[0]
                availability = compute_service.check_device_availability(
                    first_job.request.provider_name,
                    first_job.request.device_name
                )
                if availability.is_available:
                    # Device now available - move jobs to regular queue
                    for job in unavailable_jobs:
                        job.status = "QUEUED"
                        self._publish_status_update(job, "QUEUED", {"reason": "Device now available"})

            # Filter to only QUEUED jobs for batch processing
            queued_jobs = [s for s in submissions if s.status == "QUEUED"]
            if not queued_jobs:
                continue

            # All jobs in this queue share provider and device
            first_job = queued_jobs[0]
            strategy = first_job.request.strategy
            
            # Determine threshold
            wait_limit = COST_STRATEGY_WAIT_TIME if strategy == OptimizationStrategy.COST else TIME_STRATEGY_WAIT_TIME
            batch_ready = False
            
            # Criteria 1: Max batch size reached
            if len(queued_jobs) >= MAX_BATCH_SIZE:
                batch_ready = True
            
            # Criteria 2: Timeout reached for the OLDEST job
            elif (current_time - first_job.created_at) >= wait_limit:
                batch_ready = True
            
            if batch_ready:
                # Take up to MAX_BATCH_SIZE jobs
                batch = queued_jobs[:MAX_BATCH_SIZE]
                # Remove batch from pending
                remaining = [s for s in submissions if s not in batch]
                self._pending_jobs[key] = remaining
                self._execute_batch(batch)

    def _execute_batch(self, batch: List[JobSubmission]):
        if not batch:
            return

        provider_name = batch[0].request.provider_name
        device_name = batch[0].request.device_name
        
        # Check if this is a Python code batch (execute individually)
        python_code_jobs = [sub for sub in batch if sub.is_python_code]
        regular_jobs = [sub for sub in batch if not sub.is_python_code]

        # Execute Python code jobs individually
        for sub in python_code_jobs:
            try:
                provider_job_id = compute_service.execute_python_code(
                    provider_name,
                    sub.request.task,  # task contains the code
                    device_name,
                    sub.request.shots
                )
                sub.status = "SUBMITTED"
                sub.provider_job_id = provider_job_id
                self._persist_job(sub)
                self._publish_status_update(sub, "SUBMITTED")
            except Exception as e:
                logger.error(f"Python code execution failed for job {sub.id}: {e}")
                sub.status = "FAILED"
                self._persist_job(sub)
                self._publish_status_update(sub, "FAILED", extra_data={"error": str(e)})

        # Execute regular jobs as batch
        if regular_jobs:
            tasks = [sub.request.task for sub in regular_jobs]

            try:
                provider_job_ids = compute_service.execute_batch(
                    provider_name,
                    tasks,
                    device_name,
                    shots=regular_jobs[0].request.shots
                )

                # Update submissions
                for sub, p_id in zip(regular_jobs, provider_job_ids):
                    sub.status = "SUBMITTED"
                    sub.provider_job_id = p_id
                    self._persist_job(sub)
                    self._publish_status_update(sub, "SUBMITTED")

            except Exception as e:
                logger.error(f"Batch execution failed: {e}")
                for sub in regular_jobs:
                    sub.status = "FAILED"
                    self._persist_job(sub)
                    self._publish_status_update(sub, "FAILED", extra_data={"error": str(e)})

job_manager = JobManager()
# Start the background thread
job_manager.start()
