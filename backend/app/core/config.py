"""
Application Configuration
Defines settings, constants, and environment configurations for TestPilot backend.
"""
from typing import List
from pydantic import BaseModel


class Settings(BaseModel):
    PROJECT_NAME: str = "TestPilot"
    DESCRIPTION: str = "Automated Software Testing Platform for University Projects"
    VERSION: str = "0.1.0"
    API_PREFIX: str = "/api"
    
    # Allowed Cross-Origin Resource Sharing (CORS) origins
    # Allows Vite React development server on port 5173 to communicate with FastAPI
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]


settings = Settings()
