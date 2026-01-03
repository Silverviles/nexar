from abc import ABC, abstractmethod
from typing import Dict, Any

class MessagingClient(ABC):
    """
    Abstract base class for messaging clients.
    """

    @abstractmethod
    def get_client_name(self) -> str:
        """
        Returns the name of the messaging client.
        """
        pass

    @abstractmethod
    def publish_message(self, topic: str, message: Dict[str, Any]):
        """
        Publishes a message to a specific topic.
        """
        pass
