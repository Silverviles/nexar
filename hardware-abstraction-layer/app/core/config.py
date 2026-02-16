from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Application
    APP_NAME: str = "NEXAR HAL"
    VERSION: str = "1.0.0"

    # IBM Quantum
    IBM_QUANTUM_TOKEN: Optional[str] = None

    # IBM Classical (Cloud Functions)
    IBM_CLOUD_API_KEY: Optional[str] = None
    IBM_CF_API_HOST: str = "us-south.functions.cloud.ibm.com"
    IBM_CF_NAMESPACE: str = "_"  # Default namespace

    # AWS
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"

    # Azure
    AZURE_TENANT_ID: Optional[str] = None
    AZURE_CLIENT_ID: Optional[str] = None
    AZURE_CLIENT_SECRET: Optional[str] = None
    AZURE_LOCATION: str = "westus"

    # Google Cloud
    GOOGLE_PROJECT_ID: Optional[str] = None
    PUBSUB_TOPIC_NAME: str = "hal-job-updates"

    # Redis for job persistence
    REDIS_URL: Optional[str] = None  # e.g., "redis://localhost:6379/0"

    # Device availability thresholds
    DEVICE_QUEUE_THRESHOLD: int = 50  # Max pending jobs before device considered unavailable

    # Python code execution
    PYTHON_EXEC_TIMEOUT: int = 30  # Seconds timeout for sandboxed code execution
    SANDBOX_ALLOWED_MODULES: str = "qiskit,numpy,math"  # Comma-separated allowed modules

    class Config:
        env_file = ".env"


settings = Settings()
