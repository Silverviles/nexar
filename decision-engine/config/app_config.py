from pydantic_settings import BaseSettings
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    APP_NAME: str = "Decision Engine API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    HOST: str = "0.0.0.0"
    PORT: int = 8083
    
    # ML Model Paths (relative to project root)
    MODEL_PATH: str = str(Path(__file__).parent.parent / "ml_models" / "decision_engine_model.pkl")
    SCALER_PATH: str = str(Path(__file__).parent.parent / "ml_models" / "feature_scaler.pkl")
    
    # Database Configuration
    DATABASE_URL: str = "sqlite:///./decision_engine.db"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8080"]
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

def get_settings() -> Settings:
    return Settings()