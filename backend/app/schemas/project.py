"""
Project Pydantic Schemas
Defines request validation models and response shapes for Project CRUD operations.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict


class ProjectBase(BaseModel):
    name: str = Field(
        ...,
        min_length=2,
        max_length=100,
        description="Name of the project (2-100 characters)"
    )
    description: Optional[str] = Field(
        None,
        max_length=1000,
        description="Optional description of the project"
    )
    language: str = Field(
        "Python",
        max_length=50,
        description="Programming language (default: Python)"
    )


class ProjectCreate(ProjectBase):
    """Schema required when creating a new project."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    language: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)


class ProjectResponse(ProjectBase):
    """
    Schema returned to the client.
    Includes database-generated fields: id, status, and created_at.
    """
    id: int
    status: str
    created_at: datetime

    # ConfigDict(from_attributes=True) allows Pydantic to read data directly
    # from SQLAlchemy ORM model attributes (formerly orm_mode=True in Pydantic v1)
    model_config = ConfigDict(from_attributes=True)
