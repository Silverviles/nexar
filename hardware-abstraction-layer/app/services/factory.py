from app.providers.aws import AWSProvider
from app.providers.azure import AzureProvider
from app.providers.ibm import IBMProvider
from app.services.quantum_service import QuantumService


def create_quantum_service() -> QuantumService:
    """
    Factory function to create and configure the QuantumService.
    """
    service = QuantumService()
    service.register_provider(AWSProvider())
    service.register_provider(AzureProvider())
    service.register_provider(IBMProvider())
    return service


quantum_service = create_quantum_service()
