# TestPilot – Architectural Decision Records (ADR)

This document records the foundational architectural and technical decisions made for **TestPilot**, outlining the context, alternatives considered, and rationale.

---

## 📑 Index of Decisions
- [ADR-001: Client-Server Architecture with Decoupled Sandbox](#adr-001-client-server-architecture-with-decoupled-sandbox)
- [ADR-002: Backend Framework Selection: FastAPI](#adr-002-backend-framework-selection-fastapi)
- [ADR-003: Frontend Stack Selection: React + Vite + TypeScript + Tailwind CSS](#adr-003-frontend-stack-selection-react--vite--typescript--tailwind-css)
- [ADR-004: Execution Engine: Docker Sandboxing with Pytest](#adr-004-execution-engine-docker-sandboxing-with-pytest)
- [ADR-005: Database Selection: SQLite with SQLAlchemy ORM](#adr-005-database-selection-sqlite-with-sqlalchemy-orm)
- [ADR-006: Reporting Engine: ReportLab for Programmatic PDF Generation](#adr-006-reporting-engine-reportlab-for-programmatic-pdf-generation)
- [ADR-007: Standardized Predefined Project Directory Convention](#adr-007-standardized-predefined-project-directory-convention)
- [ADR-008: Modular Backend Structure with Schemas, Routes, and Config](#adr-008-modular-backend-structure-with-schemas-routes-and-config)
- [ADR-009: Centralized Frontend API Service Configuration](#adr-009-centralized-frontend-api-service-configuration)
- [ADR-010: SQLAlchemy 2.0 ORM with Dependency Session Management](#adr-010-sqlalchemy-20-orm-with-dependency-session-management)
- [ADR-011: Argon2id Password Hashing and Stateless JWT Authentication](#adr-011-argon2id-password-hashing-and-stateless-jwt-authentication)
- [ADR-012: Multi-Tenant Project Authorization via Foreign Key Ownership](#adr-012-multi-tenant-project-authorization-via-foreign-key-ownership)
- [ADR-013: Defense-in-Depth ZIP Extraction and Static Project Validation](#adr-013-defense-in-depth-zip-extraction-and-static-project-validation)

---

## ADR-013: Defense-in-Depth ZIP Extraction and Static Project Validation
- **Status:** Accepted (Day 6)
- **Context:** Untrusted user-uploaded ZIP archives present critical attack vectors: Zip Slip (path traversal outside target directory), Zip Bombs (extreme compression ratio causing disk/memory exhaustion), and disguised executables.
- **Decision:**
  - Enforce bounded stream reading (10 MB upload ceiling) to prevent memory exhaustion before saving.
  - Inspect ZIP magic header bytes (`PK\x03\x04` / `PK\x05\x06`) rather than trusting client-supplied file extensions or MIME types.
  - Defend against Zip Slip by resolving every entry's path and asserting it is strictly relative to the target extraction root using `pathlib.Path.relative_to()`.
  - Cap total uncompressed size at 50 MB, individual files at 10 MB, entry count at 500, and reject archives exceeding a 100:1 compression ratio.
  - Reject POSIX symbolic links (`0o120000`).
  - Extract into an isolated, internal directory: `uploads/projects/user_{id}/{uuid}/`.
  - Enforce static structure validation (`src/` with `.py` files and `tests/` with `test_*.py` files) **without executing any code or installing dependencies**.
  - Prune temporary directories on any validation failure.
- **Consequences:** Safe, predictable file ingestion with zero risk of host filesystem compromise.
