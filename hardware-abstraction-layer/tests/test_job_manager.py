import time
import unittest
from unittest.mock import patch, MagicMock
from app.models.execution import JobRequest, JobPriority, OptimizationStrategy
from app.services.job_manager import JobManager

class TestJobManager(unittest.TestCase):
    
    def setUp(self):
        self.job_manager = JobManager()
        # Mock compute_service within the job_manager module context
        self.patcher = patch("app.services.job_manager.compute_service")
        self.mock_compute_service = self.patcher.start()
        
    def tearDown(self):
        self.patcher.stop()
        self.job_manager._running = False # Stop thread loop

    def test_high_priority_execution(self):
        # Arrange
        req = JobRequest(
            task="task1",
            provider_name="test_prov",
            device_name="dev1",
            priority=JobPriority.HIGH
        )
        self.mock_compute_service.execute_batch.return_value = ["job-1"]
        self.mock_compute_service.get_job_status.return_value = "RUNNING"
        
        # Act
        job_id = self.job_manager.submit_job(req)
        
        # Assert
        # Should call execute_batch immediately
        self.mock_compute_service.execute_batch.assert_called_once()
        args, _ = self.mock_compute_service.execute_batch.call_args
        self.assertEqual(args[0], "test_prov")
        self.assertEqual(args[1], ["task1"])
        
        # Check internal status
        self.assertEqual(self.job_manager.get_job_status(job_id), "RUNNING")

    def test_batch_execution_size_trigger(self):
        # Arrange
        self.mock_compute_service.execute_batch.return_value = ["j1", "j2", "j3", "j4", "j5", "j6", "j7", "j8", "j9", "j10"]
        
        # Act: Submit 10 jobs (standard priority)
        # Note: We need to override MAX_BATCH_SIZE or submit 10. Default is 10.
        for i in range(10):
            req = JobRequest(
                task=f"task{i}",
                provider_name="prov1",
                device_name="dev1",
                priority=JobPriority.STANDARD,
                strategy=OptimizationStrategy.COST
            )
            self.job_manager.submit_job(req)
            
        # Manually trigger process instead of waiting for thread
        self.job_manager._process_queues()
        
        # Assert
        self.mock_compute_service.execute_batch.assert_called_once()
        args, _ = self.mock_compute_service.execute_batch.call_args
        self.assertEqual(len(args[1]), 10) # 10 tasks in batch

    def test_batch_execution_timeout_trigger(self):
        # Arrange
        req = JobRequest(
            task="task_wait",
            provider_name="prov1",
            device_name="dev1",
            priority=JobPriority.STANDARD,
            strategy=OptimizationStrategy.TIME
        )
        
        # Submit job
        self.job_manager.submit_job(req)
        
        # Assert not executed yet
        self.mock_compute_service.execute_batch.assert_not_called()
        
        # Manually simulate aging
        key = "prov1|dev1"
        self.job_manager._pending_jobs[key][0].created_at = time.time() - 2.0 # 2 seconds ago (Strategy threshold is 1.0)
        
        self.job_manager._process_queues()
        
        self.mock_compute_service.execute_batch.assert_called()

if __name__ == "__main__":
    unittest.main()
