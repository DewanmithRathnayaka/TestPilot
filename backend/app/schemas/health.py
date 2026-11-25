"""
Health and Application Info Schemas
"""
from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    application: str
    message: str


class InfoResponse(BaseModel):
    name: str
    description: str
    version: str
    status: str
