import unittest
from unittest.mock import patch, MagicMock
from app.providers.ibm_classical import IBMClassicalProvider
from app.models.classical_models import ClassicalTask


class TestIBMClassicalProvider(unittest.TestCase):
    
    @patch("app.providers.ibm_classical.settings")
    @patch("app.providers.ibm_classical.IAMAuthenticator")
    @patch("app.providers.ibm_classical.requests")
    def test_execute_task_success(self, mock_requests, mock_authenticator, mock_settings):
        # Arrange
        mock_settings.IBM_CLOUD_API_KEY = "fake-key"
        mock_settings.IBM_CF_API_HOST = "fake-host"
        mock_settings.IBM_CF_NAMESPACE = "fake-ns"
        
        mock_token_manager = MagicMock()
        mock_token_manager.get_token.return_value = "fake-token"
        mock_authenticator.return_value.token_manager = mock_token_manager

        # Mock Create Action response
        mock_put_resp = MagicMock()
        mock_put_resp.status_code = 200
        mock_requests.put.return_value = mock_put_resp

        # Mock Invoke Action response
        mock_post_resp = MagicMock()
        mock_post_resp.status_code = 202
        mock_post_resp.json.return_value = {"activationId": "act-123"}
        mock_requests.post.return_value = mock_post_resp

        provider = IBMClassicalProvider()
        task = ClassicalTask(code="print('hello')", language="python")

        # Act
        job_id = provider.execute_task(task)

        # Assert
        self.assertEqual(job_id, "act-123")
        mock_requests.put.assert_called_once()
        mock_requests.post.assert_called_once()
        # Verify headers used token
        args, kwargs = mock_requests.put.call_args
        self.assertEqual(kwargs['headers']['Authorization'], "Bearer fake-token")

    @patch("app.providers.ibm_classical.settings")
    @patch("app.providers.ibm_classical.IAMAuthenticator")
    @patch("app.providers.ibm_classical.requests")
    def test_get_job_result_success(self, mock_requests, mock_authenticator, mock_settings):
        # Arrange
        mock_settings.IBM_CLOUD_API_KEY = "fake-key"
        
        mock_get_resp = MagicMock()
        mock_get_resp.status_code = 200
        mock_get_resp.json.return_value = {"status": "success", "result": "done"}
        mock_requests.get.return_value = mock_get_resp
        
        provider = IBMClassicalProvider()
        # Pre-populate map to test cleanup
        provider._job_action_map["act-123"] = "action-abc"

        # Act
        result = provider.get_job_result("act-123")

        # Assert
        self.assertEqual(result, {"status": "success", "result": "done"})
        mock_requests.delete.assert_called_once() # Should delete the action

if __name__ == "__main__":
    unittest.main()
