"""
Project Pydantic Schemas
Defines request validation models and response shapes for Project CRUD and Upload operations.
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
    """Schema required when manually creating a project record."""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating an existing project (all fields optional)."""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, max_length=1000)
    language: Optional[str] = Field(None, max_length=50)
    status: Optional[str] = Field(None, max_length=50)


class ProjectResponse(ProjectBase):
    """
    Safe schema returned to the client.
    Includes database-generated fields and validation statistics.
    NOTE: storage_path is strictly excluded to prevent internal filesystem disclosure.
    """
    id: int
    status: str
    created_at: datetime
    user_id: Optional[int] = None
    original_filename: Optional[str] = None
    source_file_count: int = 0
    test_file_count: int = 0
    validation_status: str = "Pending"

    model_config = ConfigDict(from_attributes=True)
