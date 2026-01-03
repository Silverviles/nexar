import json
from typing import Dict, Any

from google.cloud import pubsub_v1

from app.core.config import settings
from app.messaging.base import MessagingClient


class GooglePubSubClient(MessagingClient):
    """
    Messaging client for Google Cloud Pub/Sub.
    """

    def __init__(self, project_id: str):
        self.project_id = project_id
        try:
            self.publisher = pubsub_v1.PublisherClient()
        except Exception as e:
            print(f"Could not initialize Google Pub/Sub client: {e}")
            self.publisher = None

    def get_client_name(self) -> str:
        return "google_pubsub"

    def publish_message(self, topic_name: str, message: Dict[str, Any]):
        if not self.publisher:
            print("Pub/Sub publisher not initialized. Cannot publish message.")
            return

        if not self.project_id:
            print("Google Project ID not set. Cannot publish message.")
            return
            
        topic_path = self.publisher.topic_path(self.project_id, topic_name)
        
        # Message data must be a bytestring.
        data = json.dumps(message, default=str).encode("utf-8")

        try:
            future = self.publisher.publish(topic_path, data)
            # Block until the message is published.
            future.result()
        except Exception as e:
            # In a real app, you'd want more robust error handling,
            # perhaps with retries or dead-letter queues.
            print(f"Failed to publish message to {topic_path}: {e}")

