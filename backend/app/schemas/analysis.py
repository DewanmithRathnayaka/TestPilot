"""
Project Static Analysis Schemas
Defines request and response shapes for static code structure inspection,
AST syntax validation, test candidate discovery, and dependency inspection.
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class SyntaxErrorDetail(BaseModel):
    """Details of a static syntax error detected via Python AST parsing."""
    file: str = Field(..., description="Relative path of the file containing the syntax error")
    line: Optional[int] = Field(None, description="Line number where the syntax error was detected")
    column: Optional[int] = Field(None, description="Column offset of the syntax error")
    message: str = Field(..., description="Descriptive explanation of the syntax error")


class ProjectAnalysisResponse(BaseModel):
    """
    Comprehensive static analysis summary returned to client.
    Excludes all internal filesystem paths to maintain security.
    """
    project_id: int
    project_name: str
    language: str = "Python"
    test_framework: str = "Pytest"
    analysis_status: str = Field(..., description="'completed' or 'failed'")
    structure_valid: bool = Field(..., description="Whether required src/ and tests/ directories exist")
    
    # File discovery metrics
    source_file_count: int = Field(0, description="Total Python source files discovered in src/")
    test_file_count: int = Field(0, description="Total Pytest test files discovered in tests/")
    python_file_count: int = Field(0, description="Total Python (.py) files in the project")
    total_file_count: int = Field(0, description="Total files of all types discovered")
    total_project_size: int = Field(0, description="Total size of project files in bytes")

    # AST Test candidate discovery metrics
    test_function_count: int = Field(0, description="Top-level functions matching test_*")
    test_class_count: int = Field(0, description="Classes matching Test*")
    test_method_count: int = Field(0, description="Methods inside Test* classes matching test_*")

    # AST Syntax validation metrics
    syntax_error_count: int = Field(0, description="Number of files containing syntax errors")
    syntax_errors: List[SyntaxErrorDetail] = Field(default_factory=list, description="List of detected syntax errors")

    # Dependency inspection metrics
    dependencies: List[str] = Field(default_factory=list, description="Extracted packages from requirements.txt")
    has_pytest: bool = Field(False, description="Whether Pytest is declared in requirements.txt")
    has_requirements_file: bool = Field(False, description="Whether requirements.txt is present")
    has_readme: bool = Field(False, description="Whether README.md is present")

    # Diagnostic warnings
    warnings: List[str] = Field(default_factory=list, description="Actionable advisory warnings")
    analysis_timestamp: datetime = Field(..., description="UTC timestamp when static analysis was performed")
