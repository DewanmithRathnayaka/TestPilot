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

---

## ADR-001: Client-Server Architecture with Decoupled Sandbox
- **Status:** Accepted
- **Context:** TestPilot must serve student users via a web browser while safely processing untrusted Python code submissions on the server side.
- **Decision:** Separate the presentation layer (Single Page Application in React) from the backend API (FastAPI) and isolate code execution in an asynchronous Docker sandbox worker.
- **Consequences:** Clean separation of concerns; backend remains responsive even when long-running test suites are executing; frontend and backend can be developed and maintained independently.

---

## ADR-002: Backend Framework Selection: FastAPI
- **Status:** Accepted
- **Context:** The backend must handle file uploads, manage async sub-processes, authenticate users, and parse structured execution reports.
- **Alternatives Considered:** Flask, Django, Node.js (Express).
- **Rationale:**
  - *FastAPI vs. Flask:* Flask is lightweight but lacks native async support and automatic request validation. FastAPI includes built-in Pydantic validation and automatic interactive OpenAPI/Swagger documentation.
  - *FastAPI vs. Django:* Django is feature-rich but heavyweight with significant boilerplate not needed for our API-driven architecture.
  - *Python Ecosystem:* TestPilot analyzes Python code and Pytest reports; using Python on the backend allows direct AST parsing and seamless tooling integration.
- **Consequences:** Fast development velocity, strict data validation, and self-documenting API endpoints.

---

## ADR-003: Frontend Stack Selection: React + Vite + TypeScript + Tailwind CSS
- **Status:** Accepted
- **Context:** The UI requires real-time feedback (loading states, test progress, collapsible stack traces) and clean visual presentation.
- **Alternatives Considered:** Vanilla HTML/JS, Angular, Vue.js, Plain CSS.
- **Rationale:**
  - *React:* Industry-standard component model ideal for building modular dashboards (Upload Widget, Test Summary Card, History Table).
  - *Vite:* Near-instantaneous server startup and Hot Module Replacement (HMR) compared to legacy Webpack.
  - *TypeScript:* Prevents runtime bugs by enforcing compile-time type safety on API responses.
  - *Tailwind CSS:* Utility-first CSS eliminates CSS file sprawl and enables rapid responsive design.
- **Consequences:** Modern developer experience and easily maintainable frontend codebase.

---

## ADR-004: Execution Engine: Docker Sandboxing with Pytest
- **Status:** Accepted
- **Context:** Untrusted user code can contain bugs, infinite loops, or malicious calls (`os.system("rm -rf /")`, socket connections).
- **Alternatives Considered:** Direct host `subprocess.run()`, Python `venv`, WebAssembly (Wasm).
- **Rationale:**
  - Running on the host directly or within a simple `venv` provides zero security boundary; untrusted code can read environment variables, alter files, or crash the server.
  - Docker provides real Linux OS-level isolation via kernel namespaces and cgroups. We can disable networking (`--network none`), cap memory (`256m`), cap CPU (`0.5`), and run as an unprivileged user.
  - Pytest is the gold standard testing framework in the Python community, supporting standardized test discovery and structured JSON/JUnit output.
- **Consequences:** Absolute host protection and reproducible test environments matching university grading standards.

---

## ADR-005: Database Selection: SQLite with SQLAlchemy ORM
- **Status:** Accepted
- **Context:** We need to store user accounts, project metadata, and test run records without complex infrastructure overhead during initial development.
- **Alternatives Considered:** PostgreSQL, MySQL, MongoDB.
- **Rationale:**
  - SQLite is serverless, zero-configuration, and stores data in a single local file. This eliminates external database server setup for undergraduate development.
  - Using **SQLAlchemy ORM** abstracts SQL queries into Python classes. If production scaling requires PostgreSQL in the future, only the database connection string needs to change.
- **Consequences:** Frictionless setup for Day 1–21 development with zero database maintenance friction.

---

## ADR-006: Reporting Engine: ReportLab for Programmatic PDF Generation
- **Status:** Accepted
- **Context:** Evaluators and students require an exportable official summary of test runs for academic records.
- **Alternatives Considered:** HTML-to-PDF (WeasyPrint / Puppeteer), Client-side PDF libraries (jsPDF).
- **Rationale:**
  - ReportLab is a battle-tested native Python library for generating pixel-perfect, secure PDF documents without running a headless browser.
  - Generates reports server-side, ensuring consistent styling regardless of student browser or operating system.
- **Consequences:** Reliable PDF generation without heavy headless browser dependencies.

---

## ADR-007: Standardized Predefined Project Directory Convention
- **Status:** Accepted
- **Context:** Student submissions can arrive in chaotic file hierarchies, leading to broken import paths and test discovery failures.
- **Decision:** Mandate the following project layout:
  ```text
  project_name/
  ├── src/
  ├── tests/
  ├── requirements.txt
  └── README.md
  ```
- **Rationale:**
  - Standardizes automated test discovery: Pytest knows precisely where to look (`tests/`) and `PYTHONPATH` can be deterministically set to `src/`.
  - Simplifies validation logic and error feedback: Students receive clear, actionable feedback if `src/` or `tests/` is missing.
  - Mimics professional Python packaging standards.
- **Consequences:** Eliminates parsing edge cases; keeps the MVP scope focused and achievable within 21 days.
