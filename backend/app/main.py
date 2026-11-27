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

# 1. Auto-create missing database tables
Base.metadata.create_all(bind=engine)

# 2. Safe Schema Migration Check
# Automatically adds missing columns without deleting existing data
def apply_migrations():
    with engine.connect() as conn:
        result = conn.execute(text("PRAGMA table_info(projects);"))
        columns = [row[1] for row in result.fetchall()]
        
        # Day 5 migration: user_id foreign key
        if "user_id" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN user_id INTEGER REFERENCES users(id);"))
        
        # Day 6 migrations: upload and validation metadata
        if "original_filename" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN original_filename VARCHAR(255);"))
        if "storage_path" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN storage_path VARCHAR(500);"))
        if "source_file_count" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN source_file_count INTEGER DEFAULT 0 NOT NULL;"))
        if "test_file_count" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN test_file_count INTEGER DEFAULT 0 NOT NULL;"))
        if "validation_status" not in columns:
            conn.execute(text("ALTER TABLE projects ADD COLUMN validation_status VARCHAR(50) DEFAULT 'Pending' NOT NULL;"))
            
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
        "upload": f"{settings.API_PREFIX}/projects/upload",
        "docs": "/docs"
    }
