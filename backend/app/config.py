from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = "mongodb://localhost:27017"
    MONGODB_DB_NAME: str = "clinic_db"
    
    # JWT Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Twilio Configuration
    TWILIO_ACCOUNT_SID: str
    TWILIO_AUTH_TOKEN: str
    TWILIO_FROM_PATIENT: str
    TWILIO_FROM_DOCTOR: str
    
    # Application Configuration
    BACKEND_URL: str = "http://localhost:8000"
    UPLOAD_DIR: str = "./uploads"
    
    # APScheduler Configuration
    SCHEDULER_JOBSTORE_URL: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Allow extra env vars (like DOCTOR_* credentials) without validation errors


settings = Settings()
