"""
Project API Router
Implements CRUD endpoints for managing projects stored in the SQLite database:
- POST   /api/projects             (Create project)
- GET    /api/projects             (List all projects)
- GET    /api/projects/{id}        (Retrieve single project)
- PUT    /api/projects/{id}        (Update project)
- DELETE /api/projects/{id}        (Delete project)
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project"
)
def create_project(
    payload: ProjectCreate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Creates a new project record in SQLite.
    Validates payload using Pydantic, creates a SQLAlchemy Project instance,
    commits it to the database, and returns the persisted entity.
    """
    new_project = Project(
        name=payload.name,
        description=payload.description,
        language=payload.language,
        status="Uploaded"  # Initial state per Day 4 specification
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)  # Refreshes instance with DB-generated attributes (id, created_at)
    return new_project


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all projects"
)
def get_all_projects(
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    """
    Retrieves all projects from SQLite ordered by creation time descending.
    Returns an empty list [] if no projects exist.
    """
    projects = db.query(Project).order_by(Project.created_at.desc()).all()
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single project by ID"
)
def get_project_by_id(
    project_id: int,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Retrieves a single project by its primary key ID.
    Raises HTTP 404 Not Found if the project does not exist.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )
    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing project"
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Updates mutable fields of an existing project.
    Raises HTTP 404 Not Found if the project does not exist.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    # Apply updates only for provided fields
    if payload.name is not None:
        project.name = payload.name
    if payload.description is not None:
        project.description = payload.description
    if payload.language is not None:
        project.language = payload.language
    if payload.status is not None:
        project.status = payload.status

    db.commit()
    db.refresh(project)
    return project


@router.delete(
    "/{project_id}",
    status_code=status.HTTP_200_OK,
    summary="Delete a project by ID"
)
def delete_project(
    project_id: int,
    db: Session = Depends(get_db)
):
    """
    Deletes a project record from SQLite.
    Raises HTTP 404 Not Found if the project does not exist.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    db.delete(project)
    db.commit()
    return {
        "success": True,
        "message": f"Project '{project.name}' (ID #{project_id}) was successfully deleted.",
        "id": project_id
    }
