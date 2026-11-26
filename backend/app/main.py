"""
TestPilot Main Application Entrypoint
Initializes FastAPI, mounts CORS middleware, ensures DB tables exist, runs safe schema migrations,
and registers API routers.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.core.config import settings
from app.db.session import engine, Base
import app.models.user     # Ensures User model is discovered by SQLAlchemy
import app.models.project  # Ensures Project model is discovered by SQLAlchemy
from app.api.routes import router as general_router
from app.api.projects import router as projects_router
from app.api.auth import router as auth_router

# 1. Auto-create missing database tables (creates 'users' table if not present)
Base.metadata.create_all(bind=engine)

# 2. Safe Schema Migration Check for Day 5
# Ensures the 'user_id' column exists on 'projects' table without deleting existing records
def apply_migrations():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(projects);"))
        columns = [row[1] for row in result.fetchall()]
        if "user_id" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN user_id INTEGER REFERENCES users(id);"))
            conn.commit()

apply_migrations()

# Initialize core FastAPI application
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
app.include_router(auth_router, prefix=settings.API_PREFIX)
app.include_router(projects_router, prefix=settings.API_PREFIX)


@app.get("/", tags=["Root"])
def root_redirect():
    """
    Root redirect / informational index.
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME} Backend",
        "health": f"{settings.API_PREFIX}/health",
        "auth": f"{settings.API_PREFIX}/auth/login",
        "projects": f"{settings.API_PREFIX}/projects",
        "docs": "/docs"
    }
