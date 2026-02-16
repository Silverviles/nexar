"""
Tests for IBM Quantum Python code execution and job scheduling features.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
import time

from app.providers.ibm_quantum import IBMQuantumProvider, SandboxTimeoutError
from app.models.execution import DeviceAvailability, PythonCodeRequest, JobSubmission, JobRequest
from app.services.job_manager import JobManager, RedisClient


class TestIBMQuantumPythonExecution:
    """Test sandboxed Python code execution."""

    @pytest.fixture
    def provider(self):
        """Create a mock IBM Quantum provider."""
        with patch('app.providers.ibm_quantum.QiskitRuntimeService') as mock_service:
            mock_service.return_value = MagicMock()
            provider = IBMQuantumProvider()
            return provider

    def test_create_sandbox_namespace(self, provider):
        """Test sandbox namespace includes required components."""
        namespace = provider._create_sandbox_namespace()

        # Check restricted builtins
        assert '__builtins__' in namespace
        builtins = namespace['__builtins__']
        assert 'print' in builtins
        assert 'range' in builtins
        assert 'len' in builtins

        # Dangerous builtins should NOT be present
        assert 'open' not in builtins
        assert 'eval' not in builtins
        assert 'exec' not in builtins
        assert '__import__' not in builtins

        # Qiskit components should be present
        assert 'QuantumCircuit' in namespace
        assert 'QuantumRegister' in namespace
        assert 'ClassicalRegister' in namespace

        # Math should be present
        assert 'math' in namespace
        assert 'pi' in namespace
        assert 'sqrt' in namespace

    def test_execute_sandboxed_code_valid_circuit(self, provider):
        """Test executing valid Python code that creates a circuit."""
        code = """
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.cx(0, 1)
circuit.measure([0, 1], [0, 1])
"""
        namespace = provider._create_sandbox_namespace()
        circuit = provider._execute_sandboxed_code(code, namespace, {})

        assert circuit is not None
        assert circuit.num_qubits == 2
        assert circuit.num_clbits == 2

    def test_execute_sandboxed_code_missing_circuit(self, provider):
        """Test error when code doesn't define 'circuit' variable."""
        code = """
qc = QuantumCircuit(2, 2)
qc.h(0)
"""
        namespace = provider._create_sandbox_namespace()

        with pytest.raises(ValueError, match="Code must define a 'circuit' variable"):
            provider._execute_sandboxed_code(code, namespace, {})

    def test_execute_sandboxed_code_wrong_type(self, provider):
        """Test error when 'circuit' is not a QuantumCircuit."""
        code = """
circuit = "not a circuit"
"""
        namespace = provider._create_sandbox_namespace()

        with pytest.raises(ValueError, match="'circuit' must be a QuantumCircuit"):
            provider._execute_sandboxed_code(code, namespace, {})

    def test_execute_sandboxed_code_syntax_error(self, provider):
        """Test error handling for syntax errors in user code."""
        code = """
circuit = QuantumCircuit(2 2)  # Missing comma
"""
        namespace = provider._create_sandbox_namespace()

        with pytest.raises(ValueError, match="Syntax error"):
            provider._execute_sandboxed_code(code, namespace, {})

    def test_execute_sandboxed_code_uses_math(self, provider):
        """Test that math functions work in sandbox."""
        code = """
# Use pre-loaded math functions (no import needed)
circuit = QuantumCircuit(1)
circuit.rx(pi / 2, 0)  # Using pi from namespace
circuit.ry(sqrt(2), 0)  # Using sqrt from namespace
"""
        namespace = provider._create_sandbox_namespace()
        circuit = provider._execute_sandboxed_code(code, namespace, {})

        assert circuit is not None
        assert circuit.num_qubits == 1


class TestDeviceAvailability:
    """Test device availability checking."""

    @pytest.fixture
    def provider(self):
        """Create a mock IBM Quantum provider."""
        with patch('app.providers.ibm_quantum.QiskitRuntimeService') as mock_service:
            mock_service.return_value = MagicMock()
            provider = IBMQuantumProvider()
            return provider

    def test_check_device_availability_available(self, provider):
        """Test device availability when device is available."""
        mock_backend = MagicMock()
        mock_status = MagicMock()
        mock_status.operational = True
        mock_status.pending_jobs = 10
        mock_backend.status.return_value = mock_status
        provider.service.backend.return_value = mock_backend

        with patch('app.providers.ibm_quantum.settings') as mock_settings:
            mock_settings.DEVICE_QUEUE_THRESHOLD = 50

            availability = provider.check_device_availability("ibm_brisbane")

        assert availability.device_name == "ibm_brisbane"
        assert availability.is_operational is True
        assert availability.pending_jobs == 10
        assert availability.is_available is True

    def test_check_device_availability_busy(self, provider):
        """Test device availability when device is busy (above threshold)."""
        mock_backend = MagicMock()
        mock_status = MagicMock()
        mock_status.operational = True
        mock_status.pending_jobs = 100
        mock_backend.status.return_value = mock_status
        provider.service.backend.return_value = mock_backend

        with patch('app.providers.ibm_quantum.settings') as mock_settings:
            mock_settings.DEVICE_QUEUE_THRESHOLD = 50

            availability = provider.check_device_availability("ibm_brisbane")

        assert availability.is_operational is True
        assert availability.pending_jobs == 100
        assert availability.is_available is False

    def test_check_device_availability_not_operational(self, provider):
        """Test device availability when device is not operational."""
        mock_backend = MagicMock()
        mock_status = MagicMock()
        mock_status.operational = False
        mock_status.pending_jobs = 5
        mock_backend.status.return_value = mock_status
        provider.service.backend.return_value = mock_backend

        with patch('app.providers.ibm_quantum.settings') as mock_settings:
            mock_settings.DEVICE_QUEUE_THRESHOLD = 50

            availability = provider.check_device_availability("ibm_brisbane")

        assert availability.is_operational is False
        assert availability.is_available is False


class TestJobScheduling:
    """Test job scheduling functionality."""

    @pytest.fixture
    def job_manager(self):
        """Create a JobManager with mocked dependencies."""
        with patch('app.services.job_manager.compute_service') as mock_cs, \
             patch('app.services.job_manager.messaging_client', None):
            mock_cs.execute_python_code.return_value = "provider-job-123"
            mock_cs.check_device_availability.return_value = DeviceAvailability(
                device_name="ibm_brisbane",
                is_operational=True,
                pending_jobs=10,
                queue_threshold=50
            )

            manager = JobManager()
            manager._redis = MagicMock()
            manager._redis.is_connected = False
            yield manager

    def test_submit_scheduled_job(self, job_manager):
        """Test submitting a job for future execution."""
        future_time = datetime.now() + timedelta(hours=1)

        request = JobRequest(
            task="circuit code",
            provider_name="ibm-quantum",
            device_name="ibm_brisbane",
            shots=1024
        )

        job_id = job_manager.submit_job(request, scheduled_time=future_time)

        assert job_id is not None
        assert job_id in job_manager._scheduled_jobs
        assert job_manager._jobs[job_id].status == "SCHEDULED"

    def test_submit_python_code_job(self, job_manager):
        """Test submitting a Python code job."""
        code = """
circuit = QuantumCircuit(2, 2)
circuit.h(0)
circuit.measure_all()
"""
        job_id = job_manager.submit_python_code_job(
            code=code,
            device_name="ibm_brisbane",
            shots=1024
        )

        assert job_id is not None
        assert job_manager._jobs[job_id].is_python_code is True

    def test_cancel_scheduled_job(self, job_manager):
        """Test cancelling a scheduled job."""
        future_time = datetime.now() + timedelta(hours=1)

        request = JobRequest(
            task="circuit code",
            provider_name="ibm-quantum",
            device_name="ibm_brisbane",
            shots=1024
        )

        job_id = job_manager.submit_job(request, scheduled_time=future_time)

        success = job_manager.cancel_scheduled_job(job_id)

        assert success is True
        assert job_id not in job_manager._scheduled_jobs
        assert job_manager._jobs[job_id].status == "CANCELLED"

    def test_get_scheduled_jobs(self, job_manager):
        """Test listing scheduled jobs."""
        future_time = datetime.now() + timedelta(hours=1)

        request = JobRequest(
            task="circuit code",
            provider_name="ibm-quantum",
            device_name="ibm_brisbane",
            shots=1024
        )

        job_id = job_manager.submit_job(request, scheduled_time=future_time)

        scheduled = job_manager.get_scheduled_jobs()

        assert len(scheduled) == 1
        assert scheduled[0]["job_id"] == job_id
        assert scheduled[0]["status"] == "SCHEDULED"


class TestRedisClient:
    """Test Redis client wrapper."""

    def test_redis_fallback_to_memory(self):
        """Test that RedisClient falls back to in-memory when Redis unavailable."""
        with patch('app.services.job_manager.settings') as mock_settings:
            mock_settings.REDIS_URL = None

            client = RedisClient()

            assert client.is_connected is False

            # Test basic operations work with in-memory storage
            client.hset("test_hash", "key1", "value1")
            assert client.hget("test_hash", "key1") == "value1"

            client.hset("test_hash", "key2", "value2")
            all_values = client.hgetall("test_hash")
            assert len(all_values) == 2

    def test_redis_sorted_set_operations(self):
        """Test sorted set operations for scheduled jobs."""
        with patch('app.services.job_manager.settings') as mock_settings:
            mock_settings.REDIS_URL = None

            client = RedisClient()

            # Add jobs with timestamps
            client.zadd("scheduled", {"job1": 1000.0, "job2": 2000.0, "job3": 3000.0})

            # Get jobs ready by time
            ready = client.zrangebyscore("scheduled", 0, 1500)
            assert "job1" in ready
            assert "job2" not in ready

            # Remove executed job
            client.zrem("scheduled", "job1")
            ready = client.zrangebyscore("scheduled", 0, 5000)
            assert "job1" not in ready
            assert len(ready) == 2


class TestPythonCodeRequest:
    """Test PythonCodeRequest model."""

    def test_valid_request(self):
        """Test creating a valid PythonCodeRequest."""
        request = PythonCodeRequest(
            code="circuit = QuantumCircuit(2)",
            device_name="ibm_brisbane",
            shots=2048
        )

        assert request.code == "circuit = QuantumCircuit(2)"
        assert request.device_name == "ibm_brisbane"
        assert request.shots == 2048
        assert request.queue_if_unavailable is False
        assert request.scheduled_time is None

    def test_request_with_scheduling(self):
        """Test PythonCodeRequest with scheduling."""
        future_time = datetime.now() + timedelta(hours=2)

        request = PythonCodeRequest(
            code="circuit = QuantumCircuit(2)",
            device_name="ibm_brisbane",
            shots=1024,
            scheduled_time=future_time,
            queue_if_unavailable=True
        )

        assert request.scheduled_time == future_time
        assert request.queue_if_unavailable is True
