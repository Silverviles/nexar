from app.core.config import settings
from app.messaging.google_pubsub import GooglePubSubClient

def create_messaging_client():
    """
    Factory function to create and configure the messaging client.
    """
    # For now, we are only supporting Google Pub/Sub.
    # This can be extended to support other clients based on config.
    if settings.GOOGLE_PROJECT_ID:
        return GooglePubSubClient(project_id=settings.GOOGLE_PROJECT_ID)
    
    # Return a mock/dummy client if no real one is configured
    return None

# Global instance of the messaging client
messaging_client = create_messaging_client()
