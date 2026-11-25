"""
TestPilot Main Application Entrypoint
Initializes FastAPI, mounts CORS middleware, and includes API routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import router as api_router

# Initialize the core FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS)
# This permits our React frontend running on port 5173 to safely make API calls
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the modular API router under the configured prefix (/api)
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def root_redirect():
    """
    Root redirect / informational index.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} Backend",
        "health": f"{settings.API_PREFIX}/health",
        "docs": "/docs"
    }
