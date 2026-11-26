"""
Application Configuration
Defines settings, constants, and environment configurations for TestPilot backend.
"""
import os
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "TestPilot"
    DESCRIPTION: str = "Automated Software Testing Platform for University Projects"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # SQLite Database URL
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./testpilot.db")
    
    # JWT Authentication Settings
    # Minimum 32-byte secret key for HS256 HMAC encryption
    JWT_SECRET_KEY: str = os.getenv(
        "JWT_SECRET_KEY",
        "testpilot-development-secret-key-32-bytes-minimum!!"
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    
    # Allowed Cross-Origin Resource Sharing (CORS) origins
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
