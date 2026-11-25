"""
Test Message Schemas
Demonstrates Pydantic validation: required fields, min/max length, and clear errors.
"""
from pydantic import BaseModel, Field


class TestMessageRequest(BaseModel):
    username: str = Field(
        ...,
        min_length=2,
        max_length=50,
        description="Name of the user sending the test message (2-50 characters)"
    )
    message: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="The content of the message to test (3-500 characters)"
    )


class TestMessageResponse(BaseModel):
    success: bool
    confirmation: str
    echo: TestMessageRequest
