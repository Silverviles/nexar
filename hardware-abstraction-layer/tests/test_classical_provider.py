from app.models.classical_models import ClassicalTask
from app.providers.local import LocalClassicalProvider


def test_local_classical_provider_execution():
    provider = LocalClassicalProvider()

    # Test valid python code
    task = ClassicalTask(code="print('Hello World')", language="python")
    job_id = provider.execute_task(task)

    assert job_id is not None
    assert provider.get_job_status(job_id) == "COMPLETED"

    result = provider.get_job_result(job_id)
    assert result["stdout"].strip() == "Hello World"
    assert result["stderr"] == ""


def test_local_classical_provider_variables():
    provider = LocalClassicalProvider()

    # Test variable capture
    task = ClassicalTask(code="x = 10\ny = 20\nz = x + y", language="python")
    job_id = provider.execute_task(task)

    result = provider.get_job_result(job_id)
    assert result["variables"]["z"] == "30"


def test_local_classical_provider_error():
    provider = LocalClassicalProvider()

    # Test syntax error
    task = ClassicalTask(code="print('Unfinished string", language="python")
    job_id = provider.execute_task(task)

    assert provider.get_job_status(job_id) == "FAILED"
    result = provider.get_job_result(job_id)
    assert "error" in result
