import uuid
from typing import List, Dict, Any

import requests
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

from app.core.config import settings
from app.models.classical_models import ClassicalTask
from app.providers.base import ClassicalProvider


class IBMClassicalProvider(ClassicalProvider):
    """
    A classical provider for IBM Cloud Functions.
    """

    def __init__(self):
        self.api_host = settings.IBM_CF_API_HOST
        self.namespace = settings.IBM_CF_NAMESPACE
        self.api_key = settings.IBM_CLOUD_API_KEY
        self._authenticator = None
        # Cache to store action names associated with job_ids (activation_ids)
        # In a real app, this should be in a database/redis
        self._job_action_map: Dict[str, str] = {}

    def get_provider_name(self) -> str:
        return "ibm-classical"

    def list_devices(self) -> List[Dict[str, Any]]:
        return [
            {
                "name": "ibm_cloud_functions",
                "type": "serverless",
                "description": "IBM Cloud Functions (Python 3.9)",
                "status": "active"
            }
        ]

    def _get_headers(self) -> Dict[str, str]:
        if not self.api_key:
            return {}
        if not self._authenticator:
            self._authenticator = IAMAuthenticator(self.api_key)

        token = self._authenticator.token_manager.get_token()
        return {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    def execute_task(self, task: ClassicalTask, device_name: str = "default") -> str:
        if not self.api_key:
            raise ValueError("IBM_CLOUD_API_KEY is not set.")

        action_name = f"hal-exec-{uuid.uuid4()}"
        base_url = f"https://{self.api_host}/api/v1/namespaces/{self.namespace}"

        # 1. Create Action
        # We wrap the user's code. 
        # Requirement: The code should ideally be a function 'main(args)' for CF.
        # If the user provides raw script, we wrap it.
        if "def main" not in task.code:
            # Very basic wrapper
            wrapped_code = f"""
import sys
def main(args):
    # Capture stdout? Difficult in CF simple wrapper without changing user code structure
    # This is a simplified runner
    try:
{'\n'.join(['        ' + line for line in task.code.splitlines()])}
        return {{"status": "success"}}
    except Exception as e:
        return {{"error": str(e)}}
"""
        else:
            wrapped_code = task.code

        payload = {
            "exec": {
                "kind": "python:3.9",
                "code": wrapped_code
            }
        }

        create_url = f"{base_url}/actions/{action_name}"
        headers = self._get_headers()

        resp = requests.put(create_url, headers=headers, json=payload)
        if resp.status_code not in (200, 201):
            raise RuntimeError(f"Failed to create action: {resp.text}")

        # 2. Invoke Action (Async)
        invoke_url = f"{base_url}/actions/{action_name}?blocking=false"
        resp = requests.post(invoke_url, headers=headers, json=task.parameters)

        if resp.status_code != 202:
            # Try to clean up
            requests.delete(create_url, headers=headers)
            raise RuntimeError(f"Failed to invoke action: {resp.text}")

        data = resp.json()
        activation_id = data.get("activationId")

        if not activation_id:
            requests.delete(create_url, headers=headers)
            raise RuntimeError("No activationId returned.")

        # Store mapping to delete action later
        self._job_action_map[activation_id] = action_name

        return activation_id

    def get_job_status(self, job_id: str) -> str:
        if not self.api_key:
            return "UNKNOWN"

        base_url = f"https://{self.api_host}/api/v1/namespaces/{self.namespace}"
        url = f"{base_url}/activations/{job_id}"
        headers = self._get_headers()

        resp = requests.get(url, headers=headers)

        if resp.status_code == 404:
            return "RUNNING"  # Or QUEUED, assume running if not found immediately?
            # CF activations might take a moment to appear if strictly eventually consistent,
            # but usually 404 means invalid ID or not ready.
            # However, for a valid ID, 404 usually means not done/indexed yet in some views,
            # but strictly 404 is 'not found'.
            # Let's assume RUNNING if we just got the ID.

        if resp.status_code != 200:
            return "UNKNOWN"

        data = resp.json()
        # CF doesn't have a strict 'status' field like 'RUNNING', it has 'response'.
        # But if we get the activation record, it is usually done.
        # "end" field presence indicates completion.
        if "end" in data:
            return "COMPLETED"
        return "RUNNING"

    def get_job_result(self, job_id: str) -> Dict[str, Any]:
        if not self.api_key:
            return {}

        base_url = f"https://{self.api_host}/api/v1/namespaces/{self.namespace}"

        # 1. Fetch Result
        url = f"{base_url}/activations/{job_id}/result"
        headers = self._get_headers()

        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            return {"error": f"Could not fetch result: {resp.text}"}

        result = resp.json()

        # 2. Cleanup Action (if mapped)
        action_name = self._job_action_map.pop(job_id, None)
        if action_name:
            del_url = f"{base_url}/actions/{action_name}"
            requests.delete(del_url, headers=headers)

        return result
