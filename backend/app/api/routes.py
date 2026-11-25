"""
API Routes Module
Contains endpoint handlers for TestPilot's Day 2 and Day 3 requirements:
- GET  /api/health       (Health check)
- GET  /api/info         (Application information)
- GET  /api/             (Root welcome)
- POST /api/test-message (Validated POST payload)
- GET  /api/greeting     (Query parameter demonstration)
- GET  /api/items/{item_id} (Demonstrates 404 HTTPException)
"""
from fastapi import APIRouter, HTTPException, Query, status
from app.core.config import settings
from app.schemas.health import HealthResponse, InfoResponse
from app.schemas.message import TestMessageRequest, TestMessageResponse

router = APIRouter()


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Health Check",
    tags=["System"]
)
def get_health() -> HealthResponse:
    """
    Returns the real-time health status of the backend application.
    Used by the frontend to verify connectivity.
    """
    return HealthResponse(
        status="healthy",
        application=settings.PROJECT_NAME,
        message="Backend is running successfully"
    )


@router.get(
    "/info",
    response_model=InfoResponse,
    status_code=status.HTTP_200_OK,
    summary="Application Information",
    tags=["System"]
)
def get_info() -> InfoResponse:
    """
    Returns public metadata regarding the platform, including version and description.
    """
    return InfoResponse(
        name=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        status="operational"
    )


@router.get(
    "/",
    status_code=status.HTTP_200_OK,
    summary="Welcome Root API",
    tags=["System"]
)
def get_welcome():
    """
    Simple welcome message for the API root.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} REST API",
        "documentation": "/docs",
        "version": settings.VERSION
    }


@router.post(
    "/test-message",
    response_model=TestMessageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Test POST Request with Pydantic Validation",
    tags=["Testing & Validation"]
)
def post_test_message(payload: TestMessageRequest) -> TestMessageResponse:
    """
    Receives and validates a JSON request body using Pydantic.
    FastAPI guarantees that 'username' and 'message' satisfy all constraints
    (lengths, types) before this function executes.
    """
    return TestMessageResponse(
        success=True,
        confirmation=f"Message received from '{payload.username}'!",
        echo=payload
    )


@router.get(
    "/greeting",
    status_code=status.HTTP_200_OK,
    summary="Query Parameter Demonstration",
    tags=["Testing & Validation"]
)
def get_greeting(
    name: str = Query(
        "Student",
        min_length=1,
        max_length=50,
        description="The name to personalize the greeting for"
    )
):
    """
    Demonstrates query parameters: /api/greeting?name=Student
    """
    return {
        "greeting": f"Hello, {name}! Welcome to the TestPilot Automated Software Testing Platform."
    }


@router.get(
    "/items/{item_id}",
    status_code=status.HTTP_200_OK,
    summary="Demonstrate 404 Not Found HTTPException",
    tags=["Error Handling"]
)
def get_item(item_id: int):
    """
    Demonstrates HTTP error handling.
    If item_id is greater than 100, returns a simulated 404 Not Found.
    """
    if item_id > 100:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Item with ID {item_id} was not found in TestPilot database."
        )
    return {"item_id": item_id, "name": f"Sample Item #{item_id}", "status": "active"}
