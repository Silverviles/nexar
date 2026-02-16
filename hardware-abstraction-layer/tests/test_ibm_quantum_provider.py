import unittest
from unittest.mock import patch, MagicMock

from qiskit.circuit import QuantumCircuit

from app.providers.ibm_quantum import IBMQuantumProvider


class TestIbmQuantumProvider(unittest.TestCase):
    @patch("app.providers.ibm_quantum.QiskitRuntimeService")
    def test_list_devices(self, mock_qiskit_runtime_service):
        # Arrange
        mock_backend = MagicMock()
        mock_backend.name = "ibm_brisbane"
        mock_backend.version = "1.0.0"
        mock_backend.description = "A quantum device"
        mock_backend.num_qubits = 127
        mock_backend.simulator = False
        mock_backend.basis_gates = ["cx", "id", "rz", "sx", "x"]
        mock_backend.coupling_map = [[0, 1], [1, 0], [1, 2], [2, 1]]
        
        # Mock status()
        mock_status = MagicMock()
        mock_status.operational = True
        mock_status.pending_jobs = 5
        mock_backend.status.return_value = mock_status

        mock_service_instance = mock_qiskit_runtime_service.return_value
        mock_service_instance.backends.return_value = [mock_backend]

        provider = IBMQuantumProvider()

        # Act
        devices = provider.list_devices()

        # Assert
        self.assertIsInstance(devices, list)
        self.assertEqual(len(devices), 1)
        self.assertIsInstance(devices[0], dict)
        self.assertEqual(devices[0]["name"], "ibm_brisbane")
        self.assertEqual(devices[0]["version"], "1.0.0")
        self.assertEqual(devices[0]["description"], "A quantum device")
        self.assertEqual(devices[0]["num_qubits"], 127)
        self.assertFalse(devices[0]["is_simulator"])
        self.assertTrue(devices[0]["is_operational"])
        self.assertEqual(devices[0]["pending_jobs"], 5)
        
        # Check Basis Gates (Detailed)
        self.assertIsInstance(devices[0]["basis_gates"], list)
        self.assertEqual(len(devices[0]["basis_gates"]), 5)
        self.assertEqual(devices[0]["basis_gates"][0]["qiskit_name"], "cx")
        self.assertEqual(devices[0]["basis_gates"][0]["name"], "CNOT")
        
        # Check Coupling Map (Adjacency List)
        # Expected: {0: [1], 1: [0, 2], 2: [1]}
        coupling_map = devices[0]["coupling_map"]
        self.assertIsInstance(coupling_map, dict)
        self.assertEqual(coupling_map[0], [1])
        self.assertEqual(coupling_map[1], [0, 2])
        self.assertEqual(coupling_map[2], [1])

    @patch("app.providers.ibm_quantum.QiskitRuntimeService")
    def test_init_failure(self, mock_qiskit_runtime_service):
        # Arrange
        mock_qiskit_runtime_service.side_effect = Exception("Auth Error")

        # Act
        provider = IBMQuantumProvider()

        # Assert
        self.assertIsNone(provider.service)

    @patch("app.providers.ibm_quantum.Sampler")
    @patch("app.providers.ibm_quantum.Session")
    @patch("app.providers.ibm_quantum.generate_preset_pass_manager")
    @patch("app.providers.ibm_quantum.QiskitRuntimeService")
    def test_execute_circuit(
            self,
            mock_qiskit_runtime_service,
            mock_generate_preset_pass_manager,
            mock_session,
            mock_sampler,
    ):
        # Arrange
        mock_service_instance = mock_qiskit_runtime_service.return_value
        mock_backend = MagicMock()
        mock_service_instance.backend.return_value = mock_backend

        mock_pass_manager = MagicMock()
        mock_generate_preset_pass_manager.return_value = mock_pass_manager
        mock_transpiled_circuit = MagicMock()
        mock_pass_manager.run.return_value = mock_transpiled_circuit

        mock_session_instance = mock_session.return_value.__enter__.return_value
        mock_sampler_instance = mock_sampler.return_value
        mock_job = MagicMock()
        mock_job.job_id.return_value = "job_123"
        mock_sampler_instance.run.return_value = mock_job

        provider = IBMQuantumProvider()
        circuit = QuantumCircuit(1, 1)
        device_name = "ibm_brisbane"
        shots = 1024

        # Act
        job_id = provider.execute_circuit(circuit, device_name, shots)

        # Assert
        mock_service_instance.backend.assert_called_once_with(device_name)
        mock_generate_preset_pass_manager.assert_called_once_with(
            target=mock_backend.target, optimization_level=1
        )
        mock_pass_manager.run.assert_called_once_with(circuit)
        mock_session.assert_called_once_with(
            backend=mock_backend
        )
        mock_sampler.assert_called_once_with(mode=mock_session_instance)
        mock_sampler_instance.run.assert_called_once_with(
            [mock_transpiled_circuit], shots=shots
        )
        self.assertEqual(job_id, "job_123")


if __name__ == "__main__":
    unittest.main()
