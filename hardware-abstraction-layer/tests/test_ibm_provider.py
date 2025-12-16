import unittest
from unittest.mock import patch, MagicMock

from app.providers.ibm import IBMProvider


class TestIbmProvider(unittest.TestCase):
    @patch("app.providers.ibm.QiskitRuntimeService")
    def test_list_devices(self, mock_qiskit_runtime_service):
        # Arrange
        mock_backend = MagicMock()
        mock_backend.name = "ibm_brisbane"
        mock_backend.version = "1.0.0"
        mock_backend.description = "A quantum device"

        mock_service_instance = mock_qiskit_runtime_service.return_value
        mock_service_instance.backends.return_value = [mock_backend]

        provider = IBMProvider()

        # Act
        devices = provider.list_devices()

        # Assert
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 1)
        self.assertIsInstance(devices[0], dict)
        self.assertEqual(devices[0]["name"], "ibm_brisbane")
        self.assertEqual(devices[0]["version"], "1.0.0")
        self.assertEqual(devices[0]["description"], "A quantum device")


if __name__ == "__main__":
    unittest.main()
