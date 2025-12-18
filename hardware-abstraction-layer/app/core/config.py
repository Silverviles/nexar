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

    class Config:
        env_file = ".env"


settings = Settings()
