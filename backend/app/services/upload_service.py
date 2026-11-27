"""
Secure ZIP Upload, Extraction, and Structure Validation Service
Implements defense-in-depth protections against:
- Zip Slip (Path Traversal)
- Zip Bombs (Compression ratio & size explosion)
- Malformed & Disguised Archives (Magic bytes inspection)
- Unsafe Entries (Symbolic links, devices, absolute paths)
- Structure non-compliance (Ensures src/, tests/, test files exist)
"""
import io
import os
import shutil
import uuid
import zipfile
from pathlib import Path
from typing import Dict, Any, Tuple
from fastapi import UploadFile, HTTPException, status

# Security Constraints
MAX_UPLOAD_SIZE = 10 * 1024 * 1024       # 10 MB maximum compressed upload size
MAX_UNCOMPRESSED_SIZE = 50 * 1024 * 1024 # 50 MB maximum extracted total size
MAX_INDIVIDUAL_FILE_SIZE = 10 * 1024 * 1024 # 10 MB maximum single extracted file size
MAX_ARCHIVE_ENTRIES = 500                # 500 entries maximum
MAX_COMPRESSION_RATIO = 100.0            # 100:1 maximum compression ratio
ZIP_MAGIC_PREFIX = b"PK"                 # Standard ZIP file header prefix (PK\x03\x04 or PK\x05\x06)

BASE_UPLOAD_DIR = Path("uploads/projects").resolve()


def sanitize_filename(filename: str) -> str:
    """
    Strips dangerous characters from uploaded filenames for safe metadata display.
    Never used directly as a filesystem directory or file path.
    """
    if not filename:
        return "unnamed_project.zip"
    # Keep only base filename, eliminate directory paths
    base = os.path.basename(filename)
    # Strip non-alphanumeric except dots, dashes, underscores
    sanitized = "".join(c for c in base if c.isalnum() or c in (".", "-", "_")).strip()
    return sanitized if sanitized else "project.zip"


async def read_and_validate_upload_stream(file: UploadFile) -> bytes:
    """
    Reads incoming upload stream with bounded memory chunks up to MAX_UPLOAD_SIZE.
    Validates file extension, non-empty content, and ZIP magic header bytes.
    """
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file submitted."
        )

    # 1. Extension check
    if not file.filename.lower().endswith(".zip"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid file extension. Only .zip archives are supported."
        )

    # 2. Bounded streamed reading (Prevents memory exhaustion attacks)
    chunk_size = 64 * 1024  # 64 KB chunks
    total_bytes = 0
    buffer = io.BytesIO()

    while True:
        chunk = await file.read(chunk_size)
        if not chunk:
            break
        total_bytes += len(chunk)
        if total_bytes > MAX_UPLOAD_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                detail=f"File exceeds maximum allowed upload size of {MAX_UPLOAD_SIZE // (1024 * 1024)} MB."
            )
        buffer.write(chunk)

    if total_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    raw_bytes = buffer.getvalue()

    # 3. Magic Bytes Inspection (Ensures file is genuinely a ZIP archive, not an executable or text renamed to .zip)
    if not raw_bytes.startswith(ZIP_MAGIC_PREFIX):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File signature mismatch. The uploaded file is not a valid ZIP archive."
        )

    return raw_bytes


def inspect_and_extract_zip(raw_bytes: bytes, target_dir: Path) -> None:
    """
    Inspects archive entries for security violations (Zip Slip, Zip Bomb, Symlinks),
    then safely extracts files into the specified target directory.
    """
    try:
        zf = zipfile.ZipFile(io.BytesIO(raw_bytes))
    except zipfile.BadZipFile:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Corrupted or invalid ZIP archive."
        )

    entries = zf.infolist()

    # 1. Entry Count Limit
    if len(entries) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ZIP archive contains no files."
        )
    if len(entries) > MAX_ARCHIVE_ENTRIES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archive contains {len(entries)} entries, exceeding maximum limit of {MAX_ARCHIVE_ENTRIES}."
        )

    # 2. Zip Bomb & Size Explosion Protections
    total_uncompressed_size = sum(e.file_size for e in entries)
    if total_uncompressed_size > MAX_UNCOMPRESSED_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Archive uncompressed size ({total_uncompressed_size // (1024 * 1024)} MB) exceeds 50 MB limit."
        )

    compressed_size = max(len(raw_bytes), 1)
    ratio = total_uncompressed_size / compressed_size
    if ratio > MAX_COMPRESSION_RATIO:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Zip bomb detected. Compression ratio ({ratio:.1f}:1) exceeds safety threshold of 100:1."
        )

    # 3. Security Inspection for each entry
    target_dir_resolved = target_dir.resolve()
    seen_destinations = set()

    for entry in entries:
        filename = entry.filename

        # A. Path Traversal & Absolute Path Checks
        if ".." in filename.replace("\\", "/").split("/"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Path traversal detected in archive entry: {filename}"
            )
        if filename.startswith("/") or filename.startswith("\\") or (len(filename) > 1 and filename[1] == ":"):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Absolute or drive path detected in archive entry: {filename}"
            )

        # Check resolved path is strictly within target extraction directory
        dest_path = (target_dir / filename).resolve()
        try:
            dest_path.relative_to(target_dir_resolved)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Archive entry escapes destination directory: {filename}"
            )

        # B. Symlink and Special File Rejection
        # In POSIX attributes (high 16 bits), 0o120000 denotes a symbolic link
        if (entry.external_attr >> 16) & 0o170000 == 0o120000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Symbolic links are strictly prohibited: {filename}"
            )

        # C. Individual File Size Limit
        if entry.file_size > MAX_INDIVIDUAL_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File '{filename}' exceeds individual size limit of 10 MB."
            )

        # D. Duplicate / Conflicting Paths
        if dest_path in seen_destinations and not entry.is_dir():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Duplicate file path detected in archive: {filename}"
            )
        seen_destinations.add(dest_path)

    # 4. Safe Extraction
    target_dir.mkdir(parents=True, exist_ok=True)
    try:
        for entry in entries:
            # Skip directories; we create parent dirs as needed when writing files
            if entry.is_dir():
                continue
            dest_path = (target_dir / entry.filename).resolve()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(entry) as source, open(dest_path, "wb") as target:
                shutil.copyfileobj(source, target)
    except Exception as e:
        # Prune temporary files on extraction failure
        shutil.rmtree(target_dir, ignore_errors=True)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to safely extract archive: {str(e)}"
        )


def validate_project_structure(project_root: Path) -> Dict[str, Any]:
    """
    Performs static structural inspection of the extracted project directory.
    Verifies adherence to standard TestPilot layout:
      - src/ directory with at least one .py file
      - tests/ directory with at least one test_*.py or *_test.py file
      - requirements.txt (optional but checked)
    NEVER imports, executes, or runs code during validation!
    """
    # Check if files were extracted directly into project_root or inside a single top-level folder
    contents = [p for p in project_root.iterdir()]
    working_root = project_root

    # If the ZIP contained a single root directory wrapping everything (and it's not 'src' or 'tests'), unwrap it
    if len(contents) == 1 and contents[0].is_dir() and contents[0].name.lower() not in ("src", "tests"):
        working_root = contents[0]

    src_dir = working_root / "src"
    tests_dir = working_root / "tests"
    req_file = working_root / "requirements.txt"

    # 1. Directory Checks
    if not src_dir.exists() or not src_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project structure invalid: Missing required 'src/' directory."
        )
    if not tests_dir.exists() or not tests_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project structure invalid: Missing required 'tests/' directory."
        )

    # 2. Source Files Inspection
    py_source_files = list(src_dir.rglob("*.py"))
    if not py_source_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project structure invalid: 'src/' directory contains no Python (.py) source files."
        )

    # 3. Test Files Inspection
    test_files = [
        f for f in tests_dir.rglob("*.py")
        if f.name.startswith("test_") or f.name.endswith("_test.py")
    ]
    if not test_files:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project structure invalid: 'tests/' directory contains no Pytest files (must match test_*.py or *_test.py)."
        )

    return {
        "valid": True,
        "language": "Python",
        "test_framework": "Pytest",
        "source_files": len(py_source_files),
        "test_files": len(test_files),
        "has_requirements": req_file.exists() and req_file.is_file(),
        "working_root": str(working_root)
    }


async def process_project_upload(file: UploadFile, user_id: int) -> Tuple[str, str, Dict[str, Any]]:
    """
    Coordinates the complete secure upload pipeline:
    1. Read and validate upload stream.
    2. Create isolated storage directory: uploads/projects/{uuid}/
    3. Inspect and safely extract ZIP archive.
    4. Validate standard Python project layout.
    Returns: (sanitized_original_filename, relative_storage_path, validation_summary)
    """
    raw_bytes = await read_and_validate_upload_stream(file)
    sanitized_filename = sanitize_filename(file.filename or "project.zip")

    # Generate unique internal storage identifier
    storage_uuid = str(uuid.uuid4())
    user_storage_dir = BASE_UPLOAD_DIR / f"user_{user_id}" / storage_uuid

    try:
        # Extract archive securely
        inspect_and_extract_zip(raw_bytes, user_storage_dir)

        # Validate project structure statically
        validation = validate_project_structure(user_storage_dir)

        # Relative path for internal database reference
        relative_path = str(user_storage_dir.relative_to(Path.cwd()))
        return sanitized_filename, relative_path, validation

    except Exception:
        # Ensure no partial or dangerous files remain on disk if any validation fails
        shutil.rmtree(user_storage_dir, ignore_errors=True)
        raise
