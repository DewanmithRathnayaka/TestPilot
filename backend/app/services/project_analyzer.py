"""
Python Project Structure Analysis and Validation Engine
Performs purely static code inspection using Python's built-in AST and pathlib:
- Discovers source files, test files, dependencies, and README
- Detects Python syntax errors using ast.parse()
- Identifies Pytest test candidates (functions, classes, methods)
- Parses requirements.txt dependency declarations
- Emits structured warnings and quality metrics
IMPORTANT: NEVER imports, executes, or runs code (no exec, no eval, no subprocess, no importlib).
"""
import ast
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Tuple, Dict, Any, Optional
from fastapi import HTTPException, status

from app.schemas.analysis import ProjectAnalysisResponse, SyntaxErrorDetail

# Maximum allowable file size for AST reading (1 MB per file to prevent memory spikes)
MAX_INSPECT_FILE_SIZE = 1 * 1024 * 1024


def locate_working_root(base_dir: Path) -> Path:
    """
    Finds the working root directory of an extracted project.
    If the project was extracted into a single wrapper folder (e.g. project_name/src/...),
    it locates the inner folder, matching the Day 6 layout convention.
    """
    contents = [p for p in base_dir.iterdir() if not p.name.startswith(".")]
    if len(contents) == 1 and contents[0].is_dir() and contents[0].name.lower() not in ("src", "tests"):
        return contents[0]
    return base_dir


def discover_files(working_root: Path) -> Tuple[List[Path], List[Path], List[Path], List[Path], Optional[Path], Optional[Path], int]:
    """
    Recursively scans the project directory safely:
    - Ignores __pycache__, .pyc, hidden files, and symbolic links
    - Categorizes src files, test files, all python files, and total files
    - Locates requirements.txt and README.md
    - Computes total project size in bytes
    """
    src_files: List[Path] = []
    test_files: List[Path] = []
    all_py_files: List[Path] = []
    all_files: List[Path] = []
    requirements_file: Optional[Path] = None
    readme_file: Optional[Path] = None
    total_size = 0

    src_dir = working_root / "src"
    tests_dir = working_root / "tests"

    for root_str, dirs, files in os.walk(working_root, followlinks=False):
        # Ignore cache and hidden directories in-place
        dirs[:] = [d for d in dirs if d != "__pycache__" and not d.startswith(".")]

        root_path = Path(root_str)

        for filename in files:
            # Ignore hidden files, compiled python bytecode (.pyc, .pyo)
            if filename.startswith(".") or filename.endswith((".pyc", ".pyo")):
                continue

            file_path = root_path / filename

            # Reject/skip symlinks
            if file_path.is_symlink():
                continue

            try:
                file_size = file_path.stat().st_size
                total_size += file_size
            except OSError:
                continue

            all_files.append(file_path)

            # Check for requirements.txt or README at working root
            if file_path.parent == working_root:
                if filename.lower() == "requirements.txt":
                    requirements_file = file_path
                elif filename.lower().startswith("readme"):
                    readme_file = file_path

            # Python files
            if filename.endswith(".py"):
                all_py_files.append(file_path)

                # Check if file resides inside src/
                if src_dir.exists() and file_path.is_relative_to(src_dir):
                    src_files.append(file_path)

                # Check if file resides inside tests/ and matches test naming convention
                if tests_dir.exists() and file_path.is_relative_to(tests_dir):
                    if filename.startswith("test_") or filename.endswith("_test.py"):
                        test_files.append(file_path)

    return src_files, test_files, all_py_files, all_files, requirements_file, readme_file, total_size


def check_ast_syntax(file_path: Path, working_root: Path) -> Tuple[Optional[ast.AST], Optional[SyntaxErrorDetail]]:
    """
    Statically parses a Python file into an Abstract Syntax Tree using ast.parse().
    Detects syntax errors without executing the code.
    Returns (AST_tree, None) on success or (None, SyntaxErrorDetail) on syntax failure.
    """
    rel_path = str(file_path.relative_to(working_root)).replace("\\", "/")

    try:
        if file_path.stat().st_size > MAX_INSPECT_FILE_SIZE:
            return None, SyntaxErrorDetail(
                file=rel_path,
                line=0,
                column=0,
                message=f"File exceeds maximum analysis inspection size limit of {MAX_INSPECT_FILE_SIZE // 1024} KB."
            )

        with open(file_path, "r", encoding="utf-8", errors="replace") as f:
            source_content = f.read()

        # Static AST parsing: Translates Python code into syntax nodes without executing
        tree = ast.parse(source_content, filename=rel_path)
        return tree, None

    except SyntaxError as e:
        return None, SyntaxErrorDetail(
            file=rel_path,
            line=e.lineno,
            column=e.offset,
            message=e.msg or "Invalid Python syntax"
        )
    except Exception as e:
        return None, SyntaxErrorDetail(
            file=rel_path,
            line=0,
            column=0,
            message=f"Could not read or parse file: {str(e)}"
        )


def discover_pytest_candidates(tree: ast.AST) -> Tuple[int, int, int]:
    """
    Statically traverses an AST of a test file to discover candidate test items:
    - Top-level function definitions named test_*
    - Class definitions named Test*
    - Methods inside Test* classes named test_*
    NOTE: These are candidate test structures, not guaranteed executable fixtures.
    """
    test_functions = 0
    test_classes = 0
    test_methods = 0

    for node in ast.iter_child_nodes(tree):
        # 1. Top-level test function: def test_*()
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if node.name.startswith("test_"):
                test_functions += 1

        # 2. Test class: class Test*()
        elif isinstance(node, ast.ClassDef):
            if node.name.startswith("Test"):
                test_classes += 1
                for class_child in ast.iter_child_nodes(node):
                    if isinstance(class_child, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        if class_child.name.startswith("test_"):
                            test_methods += 1

    return test_functions, test_classes, test_methods


def inspect_requirements(req_path: Optional[Path]) -> Tuple[List[str], bool, List[str]]:
    """
    Statically inspects requirements.txt declarations:
    - Extracts package names and version specifiers
    - Detects whether 'pytest' is declared
    - Records warnings for malformed or suspicious lines
    Does NOT install dependencies, run pip, or access the network.
    """
    if not req_path or not req_path.exists():
        return [], False, []

    dependencies: List[str] = []
    has_pytest = False
    warnings: List[str] = []

    try:
        with open(req_path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        for idx, line in enumerate(lines, start=1):
            stripped = line.strip()
            # Ignore empty lines and full comment lines
            if not stripped or stripped.startswith("#"):
                continue

            # Strip inline comments (e.g. "pytest>=7.0 # test runner")
            clean_line = stripped.split("#")[0].strip()
            if not clean_line:
                continue

            # Extract base package name using standard PEP 508 identifier regex
            match = re.match(r"^([A-Za-z0-9_\-\.]+)", clean_line)
            if match:
                pkg_name = match.group(1).lower()
                dependencies.append(clean_line)
                if pkg_name == "pytest":
                    has_pytest = True
            else:
                warnings.append(f"requirements.txt line {idx}: Unable to parse package name: '{clean_line}'")

    except Exception as e:
        warnings.append(f"Could not read requirements.txt: {str(e)}")

    return dependencies, has_pytest, warnings


def analyze_extracted_project(storage_dir: Path, project_id: int, project_name: str) -> ProjectAnalysisResponse:
    """
    Main static analysis entrypoint.
    Inspects an already extracted project directory and returns structural,
    syntactic, test candidate, and dependency analysis metrics.
    """
    if not storage_dir.exists() or not storage_dir.is_dir():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Project files directory does not exist or has not been extracted yet."
        )

    working_root = locate_working_root(storage_dir)
    src_dir = working_root / "src"
    tests_dir = working_root / "tests"

    # 1. Structure Verification
    structure_valid = (
        src_dir.exists() and src_dir.is_dir() and
        tests_dir.exists() and tests_dir.is_dir()
    )

    # 2. File Discovery
    src_files, test_files, all_py_files, all_files, req_file, readme_file, total_size = discover_files(working_root)

    # 3. Static AST Syntax Analysis & Test Candidate Discovery
    syntax_errors: List[SyntaxErrorDetail] = []
    total_test_functions = 0
    total_test_classes = 0
    total_test_methods = 0

    for py_file in all_py_files:
        tree, err = check_ast_syntax(py_file, working_root)
        if err:
            syntax_errors.append(err)
        elif tree and py_file in test_files:
            fn_cnt, cls_cnt, meth_cnt = discover_pytest_candidates(tree)
            total_test_functions += fn_cnt
            total_test_classes += cls_cnt
            total_test_methods += meth_cnt

    # 4. Dependency Analysis
    dependencies, has_pytest, dep_warnings = inspect_requirements(req_file)

    # 5. Advisory Warnings Compilation
    warnings: List[str] = []
    warnings.extend(dep_warnings)

    if not structure_valid:
        if not (src_dir.exists() and src_dir.is_dir()):
            warnings.append("Missing required 'src/' directory.")
        if not (tests_dir.exists() and tests_dir.is_dir()):
            warnings.append("Missing required 'tests/' directory.")

    if structure_valid and len(src_files) == 0:
        warnings.append("The 'src/' directory contains no Python (.py) source files.")

    if structure_valid and len(test_files) == 0:
        warnings.append("The 'tests/' directory contains no Pytest test files (test_*.py or *_test.py).")

    if syntax_errors:
        warnings.append(f"{len(syntax_errors)} Python file(s) contain syntax errors.")

    if req_file and not has_pytest:
        warnings.append("requirements.txt was found, but 'pytest' is not declared as a dependency.")

    total_test_candidates = total_test_functions + total_test_methods
    if structure_valid and len(test_files) > 0 and total_test_candidates == 0:
        warnings.append("Test files were found, but no test functions or methods matching test_* naming were discovered.")

    return ProjectAnalysisResponse(
        project_id=project_id,
        project_name=project_name,
        language="Python",
        test_framework="Pytest",
        analysis_status="completed",
        structure_valid=structure_valid and len(src_files) > 0 and len(test_files) > 0,
        source_file_count=len(src_files),
        test_file_count=len(test_files),
        python_file_count=len(all_py_files),
        total_file_count=len(all_files),
        total_project_size=total_size,
        test_function_count=total_test_functions,
        test_class_count=total_test_classes,
        test_method_count=total_test_methods,
        syntax_error_count=len(syntax_errors),
        syntax_errors=syntax_errors,
        dependencies=dependencies,
        has_pytest=has_pytest,
        has_requirements_file=req_file is not None,
        has_readme=readme_file is not None,
        warnings=warnings,
        analysis_timestamp=datetime.now(timezone.utc)
    )
