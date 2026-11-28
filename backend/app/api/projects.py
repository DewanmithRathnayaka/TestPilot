"""
Project API Router
Implements CRUD endpoints and secure ZIP upload handling for software projects:
- POST   /api/projects/upload      (Secure ZIP upload, extraction, and validation)
- POST   /api/projects             (Manual project record creation)
- GET    /api/projects             (List user's projects)
- GET    /api/projects/{id}        (Retrieve project details)
- PUT    /api/projects/{id}        (Update project details)
- DELETE /api/projects/{id}        (Delete project record)
"""
from typing import List
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectResponse
from app.schemas.analysis import ProjectAnalysisResponse
from app.api.deps import get_current_user
from app.services.upload_service import process_project_upload
from app.services.project_analyzer import analyze_extracted_project

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post(
    "/upload",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Upload and securely validate a Python project ZIP"
)
async def upload_project_zip(
    file: UploadFile = File(..., description="ZIP archive containing Python project (src/, tests/, requirements.txt)"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Authenticated ZIP Project Upload Pipeline:
    1. Validates upload size (<= 10 MB) via bounded streaming.
    2. Inspects ZIP header magic bytes (PK\\x03\\x04).
    3. Defends against Zip Slip (Path Traversal), Zip Bombs, and Symlinks.
    4. Safely extracts files into a dedicated internal directory: uploads/projects/user_{id}/{uuid}/
    5. Statically validates project layout: verifies src/, tests/, Python files, and Pytest files.
    6. Persists project metadata to SQLite and links it to the authenticated user.
    """
    original_filename, storage_path, validation = await process_project_upload(
        file=file,
        user_id=current_user.id
    )

    # Derive clean display project name from filename
    project_name = original_filename
    if project_name.lower().endswith(".zip"):
        project_name = project_name[:-4]

    # Create persisted database record
    new_project = Project(
        name=project_name,
        description=f"Uploaded ZIP project archive: {original_filename}",
        language=validation.get("language", "Python"),
        status="Validated",
        user_id=current_user.id,
        original_filename=original_filename,
        storage_path=storage_path,
        source_file_count=validation.get("source_files", 0),
        test_file_count=validation.get("test_files", 0),
        validation_status="Valid"
    )

    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.post(
    "",
    response_model=ProjectResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new project record manually"
)
def create_project(
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Creates a new project record manually in SQLite owned by the authenticated user.
    """
    new_project = Project(
        name=payload.name,
        description=payload.description,
        language=payload.language,
        status="Uploaded",
        user_id=current_user.id,
        validation_status="Pending"
    )
    db.add(new_project)
    db.commit()
    db.refresh(new_project)
    return new_project


@router.get(
    "",
    response_model=List[ProjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Get all projects owned by the current user"
)
def get_all_projects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> List[ProjectResponse]:
    """
    Retrieves all projects owned by the currently authenticated user.
    Users cannot view projects belonging to other users.
    """
    projects = (
        db.query(Project)
        .filter(Project.user_id == current_user.id)
        .order_by(Project.created_at.desc())
        .all()
    )
    return projects


@router.get(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Get a single project by ID (Authorized)"
)
def get_project_by_id(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Retrieves a single project by its primary key ID.
    Raises 404 if not found or 403 if owned by another user.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to view this project."
        )

    return project


@router.put(
    "/{project_id}",
    response_model=ProjectResponse,
    status_code=status.HTTP_200_OK,
    summary="Update an existing project (Authorized)"
)
def update_project(
    project_id: int,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectResponse:
    """
    Updates mutable fields of an existing project owned by the current user.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to modify this project."
        )

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
    summary="Delete a project by ID (Authorized)"
)
def delete_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Deletes a project record from SQLite owned by the current user.
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to delete this project."
        )

    db.delete(project)
    db.commit()
    return {
        "success": True,
        "message": f"Project '{project.name}' (ID #{project_id}) was successfully deleted.",
        "id": project_id
    }


@router.post(
    "/{project_id}/analyze",
    response_model=ProjectAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Statically analyze an uploaded project structure, AST syntax, and test candidates"
)
def analyze_project(
    project_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> ProjectAnalysisResponse:
    """
    Statically analyzes an uploaded project without executing any code:
    - Verifies src/ and tests/ hierarchy
    - Discovers Python files, test files, dependencies, and README
    - Validates syntax using Python AST (ast.parse)
    - Discovers test functions, classes, and methods matching Pytest conventions
    - Inspects requirements.txt for pytest declaration
    - Updates project status to 'Analyzed' and synchronizes file counts
    """
    project = db.query(Project).filter(Project.id == project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Project with ID {project_id} not found."
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: You do not have permission to analyze this project."
        )

    if not project.storage_path or not Path(project.storage_path).exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project storage path does not exist on disk or files have not been uploaded."
        )

    analysis_result = analyze_extracted_project(
        storage_dir=Path(project.storage_path),
        project_id=project.id,
        project_name=project.name
    )

    # Update project record status and file metrics in SQLite
    project.status = "Analyzed"
    project.source_file_count = analysis_result.source_file_count
    project.test_file_count = analysis_result.test_file_count
    project.validation_status = (
        "Valid" if analysis_result.structure_valid and analysis_result.syntax_error_count == 0 else "Invalid"
    )
    db.commit()
    db.refresh(project)

    return analysis_result
