from app.providers.aws_classical import AWSClassicalProvider
from app.providers.aws_quantum import AWSQuantumProvider
from app.providers.azure_classical import AzureClassicalProvider
from app.providers.azure_quantum import AzureQuantumProvider
from app.providers.ibm_classical import IBMClassicalProvider
from app.providers.ibm_quantum import IBMQuantumProvider
from app.providers.local import LocalClassicalProvider
from app.services.compute_service import ComputeService


def create_compute_service() -> ComputeService:
    """
    Factory function to create and configure the ComputeService.
    """
    service = ComputeService()

    # Register Quantum Providers
    service.register_provider(AWSQuantumProvider())
    service.register_provider(AzureQuantumProvider())
    service.register_provider(IBMQuantumProvider())

    # Register Classical Providers
    service.register_provider(AWSClassicalProvider())
    service.register_provider(AzureClassicalProvider())
    service.register_provider(IBMClassicalProvider())
    service.register_provider(LocalClassicalProvider())

    return service


compute_service = create_compute_service()
