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

---

## ADR-001: Client-Server Architecture with Decoupled Sandbox
- **Status:** Accepted
- **Context:** TestPilot must serve student users via a web browser while safely processing untrusted Python code submissions on the server side.
- **Decision:** Separate the presentation layer (Single Page Application in React) from the backend API (FastAPI) and isolate code execution in an asynchronous Docker sandbox worker.
- **Consequences:** Clean separation of concerns; backend remains responsive; frontend and backend can be developed and maintained independently.

---

## ADR-002: Backend Framework Selection: FastAPI
- **Status:** Accepted
- **Context:** The backend must handle file uploads, manage async sub-processes, authenticate users, and parse structured execution reports.
- **Decision:** Use FastAPI for backend REST API development.
- **Consequences:** High-speed execution, native async capabilities, automatic request validation via Pydantic, and self-documenting OpenAPI endpoints (`/docs`).

---

## ADR-003: Frontend Stack Selection: React + Vite + TypeScript + Tailwind CSS
- **Status:** Accepted
- **Context:** The UI requires real-time feedback (loading states, test progress, collapsible stack traces) and clean visual presentation.
- **Decision:** Build client as a Single Page Application using React 18, Vite, and TypeScript.
- **Consequences:** Type safety prevents runtime UI bugs; bundle sizes remain compact (< 155 KB uncompressed); instantaneous hot reloading.

---

## ADR-004: Execution Engine: Docker Sandboxing with Pytest
- **Status:** Accepted
- **Context:** Untrusted user code can contain bugs, infinite loops, or malicious calls.
- **Decision:** Execute uploaded code inside isolated ephemeral Docker containers with `--network none`, CPU/memory quotas, and non-root user permissions.
- **Consequences:** Absolute host protection and reproducible test environments.

---

## ADR-005: Database Selection: SQLite with SQLAlchemy ORM
- **Status:** Accepted
- **Context:** Need persistent storage without the operational overhead of a standalone database server for the 21-day MVP.
- **Decision:** Use SQLite stored as a local file (`testpilot.db`) accessed via SQLAlchemy ORM.
- **Consequences:** Zero configuration; seamless future migration to PostgreSQL simply by changing the connection URL.

---

## ADR-006: Reporting Engine: ReportLab for Programmatic PDF Generation
- **Status:** Accepted
- **Context:** Evaluators and students require an exportable official summary of test runs.
- **Decision:** Use ReportLab for server-side PDF generation.
- **Consequences:** Fast, pixel-perfect PDF rendering without heavy headless browser dependencies.

---

## ADR-007: Standardized Predefined Project Directory Convention
- **Status:** Accepted
- **Context:** Student submissions can arrive in chaotic file hierarchies.
- **Decision:** Mandate the following layout: `src/`, `tests/`, `requirements.txt`, `README.md`.
- **Consequences:** Deterministic test discovery and clear validation diagnostics.

---

## ADR-008: Modular Backend Structure with Schemas, Routes, and Config
- **Status:** Accepted (Day 3)
- **Context:** A monolithic file quickly becomes unmanageable as endpoints, data validation schemas, and configurations expand.
- **Decision:** Separate backend into: `app/core/config.py`, `app/schemas/`, `app/api/`, and `app/main.py`.
- **Consequences:** Clean separation of concerns, testability, and high maintainability.

---

## ADR-009: Centralized Frontend API Service Configuration
- **Status:** Accepted (Day 3)
- **Context:** Hardcoding backend URLs across React components causes broken links when deploying.
- **Decision:** Store backend base URL in `frontend/src/config.ts` powered by Vite environment variables (`import.meta.env.VITE_API_BASE_URL`).
- **Consequences:** All components import endpoints from a single source of truth; switching environments requires only editing `.env`.

---

## ADR-010: SQLAlchemy 2.0 ORM with Dependency Session Management
- **Status:** Accepted (Day 4)
- **Context:** Managing database transactions and connection lifecycles manually inside API routes leads to connection leaks and concurrency errors.
- **Decision:** Implement SQLAlchemy 2.0 with the FastAPI dependency pattern:
  - `SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)`
  - `get_db()` generator yielding `db` and closing it in a `finally` block.
  - Enable `connect_args={"check_same_thread": False}` for SQLite multi-threaded access.
  - Decouple ORM persistence models (`app/models/`) from API contract schemas (`app/schemas/`).
- **Consequences:** Automatic session cleanup after every HTTP request; complete isolation between persistence and presentation layers.
