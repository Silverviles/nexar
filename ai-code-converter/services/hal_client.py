"""HTTP client for communicating with the Hardware Abstraction Layer (HAL)."""

import asyncio
import logging
from typing import Any, Dict, List, Optional

import httpx

from config.config import (
    HAL_URL,
    HAL_DEFAULT_DEVICE,
    HAL_POLL_INTERVAL,
    HAL_TIMEOUT,
)

logger = logging.getLogger(__name__)

TERMINAL_STATUSES = {"COMPLETED", "FAILED", "CANCELLED"}


class HALError(Exception):
    """Raised when the HAL returns an error or is unreachable."""

    def __init__(self, message: str, status_code: Optional[int] = None):
        super().__init__(message)
        self.status_code = status_code


class HALClient:
    """Async client that wraps the Hardware Abstraction Layer REST API."""

    def __init__(self, base_url: str = HAL_URL, timeout: int = HAL_TIMEOUT):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout

    def _client(self) -> httpx.AsyncClient:
        return httpx.AsyncClient(
            base_url=self._base_url,
            timeout=httpx.Timeout(self._timeout),
        )

    async def list_devices(self) -> List[Dict[str, Any]]:
        """Fetch available IBM Quantum devices from the HAL."""
        async with self._client() as client:
            resp = await client.get("/api/quantum/ibm-quantum/devices")
            if resp.status_code != 200:
                raise HALError(
                    f"Failed to list devices: {resp.text}",
                    status_code=resp.status_code,
                )
            return resp.json().get("devices", [])

    async def submit_code(
        self,
        code: str,
        device_name: Optional[str] = None,
        shots: int = 1024,
    ) -> Dict[str, Any]:
        """Submit Python code to the HAL for execution on IBM Quantum.

        The code must define a ``circuit`` variable that is a
        ``QuantumCircuit``.  Returns the initial job envelope
        (including ``job_id``).
        """
        device = device_name or HAL_DEFAULT_DEVICE
        payload = {
            "code": code,
            "device_name": device,
            "shots": shots,
        }
        async with self._client() as client:
            resp = await client.post(
                "/api/quantum/ibm-quantum/execute-python",
                json=payload,
            )
            if resp.status_code not in (200, 201):
                raise HALError(
                    f"Code submission failed: {resp.text}",
                    status_code=resp.status_code,
                )
            return resp.json()

    async def get_job_status(self, job_id: str) -> str:
        """Poll the HAL for the current status of a job."""
        async with self._client() as client:
            resp = await client.get(f"/api/jobs/ibm-quantum/{job_id}")
            if resp.status_code != 200:
                raise HALError(
                    f"Failed to get job status: {resp.text}",
                    status_code=resp.status_code,
                )
            return resp.json().get("status", "UNKNOWN")

    async def get_job_result(self, job_id: str) -> Dict[str, Any]:
        """Retrieve the result payload for a completed job."""
        async with self._client() as client:
            resp = await client.get(f"/api/jobs/ibm-quantum/{job_id}/result")
            if resp.status_code != 200:
                raise HALError(
                    f"Failed to get job result: {resp.text}",
                    status_code=resp.status_code,
                )
            return resp.json().get("result", {})

    async def execute_and_wait(
        self,
        code: str,
        device_name: Optional[str] = None,
        shots: int = 1024,
        poll_interval: int = HAL_POLL_INTERVAL,
    ) -> Dict[str, Any]:
        """Submit code, poll until completion, and return the result.

        Raises ``HALError`` if the job fails or the timeout is exceeded.
        """
        submission = await self.submit_code(code, device_name, shots)
        job_id = submission["job_id"]
        logger.info("HAL job submitted: %s on device %s", job_id, device_name or HAL_DEFAULT_DEVICE)

        elapsed = 0
        last_status = None
        while elapsed < self._timeout:
            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

            status = await self.get_job_status(job_id)
            if status != last_status:
                logger.info("HAL job %s status: %s (%ds elapsed)", job_id, status, elapsed)
                last_status = status
            else:
                logger.debug("HAL job %s still %s (%ds elapsed)", job_id, status, elapsed)

            if status in TERMINAL_STATUSES:
                if status != "COMPLETED":
                    raise HALError(f"HAL job {job_id} ended with status: {status}")
                return await self.get_job_result(job_id)

        raise HALError(
            f"HAL job {job_id} timed out after {self._timeout}s (last status: {last_status})"
        )

    async def health_check(self) -> bool:
        """Return True if the HAL is reachable and healthy."""
        try:
            async with self._client() as client:
                resp = await client.get("/api/health")
                return resp.status_code == 200
        except Exception:
            return False


hal_client = HALClient()
