"""
TestPilot Main Application Entrypoint
Initializes FastAPI, mounts CORS middleware, ensures DB tables exist, and registers API routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.session import engine, Base
import app.models.project  # Ensures SQLAlchemy discovers Project model before table creation
from app.api.routes import router as general_router
from app.api.projects import router as projects_router

# Auto-create all database tables on application startup
# In production, migrations (Alembic) are used; create_all() is ideal for rapid development.
Base.metadata.create_all(bind=engine)

# Initialize the core FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.DESCRIPTION,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure Cross-Origin Resource Sharing (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers under /api
app.include_router(general_router, prefix=settings.API_PREFIX)
app.include_router(projects_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def root_redirect():
    """
    Root redirect / informational index.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} Backend",
        "health": f"{settings.API_PREFIX}/health",
        "projects": f"{settings.API_PREFIX}/projects",
        "docs": "/docs"
    }
