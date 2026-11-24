# TestPilot – 21-Day Development Progress Tracker

This document tracks daily milestones, completed objectives, and upcoming phases across our 21-day development roadmap.

---

## 📅 Roadmap Overview

| Week | Focus Area | Status |
|---|---|---|
| **Week 1 (Days 1–7)** | Foundations, Architecture, Auth & Upload Pipeline | 🟡 In Progress (Day 1 Complete) |
| **Week 2 (Days 8–14)** | Docker Sandboxing, Pytest Engine & Result Processing | ⚪ Pending |
| **Week 3 (Days 15–21)** | Frontend Dashboard, PDF Reporting & Final Hardening | ⚪ Pending |

---

## 🚀 Daily Breakdown

### 📍 Week 1: Foundations, Architecture & Ingestion

- [x] **Day 1: Project Understanding, Requirements & System Architecture**
  - Clarified university project objectives and student learning goals.
  - Defined functional (FR-01 to FR-11) and non-functional requirements (NFR-01 to NFR-17).
  - Designed high-level client-server architecture with Docker sandbox model.
  - Mapped complete upload-to-report execution workflow and sequence diagrams.
  - Authored foundational documentation: `README.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DEVELOPMENT_PROGRESS.md`, `DECISIONS.md`.
  - Conducted 10-question fundamental knowledge check.

- [ ] **Day 2: Backend Project Setup & Environment Configuration**
  - Initialize FastAPI backend directory structure.
  - Configure Python virtual environment and dependencies (`fastapi`, `uvicorn`, `pydantic`, `sqlalchemy`).
  - Create configuration management system (`settings.py` / `.env`).
  - Build initial health check endpoint (`/api/v1/health`).

- [ ] **Day 3: Database Models & Migrations**
  - Design SQLAlchemy database schema (`User`, `Project`, `TestRun`, `TestResult`).
  - Setup SQLite database connection and session management.
  - Implement base CRUD helper functions.

- [ ] **Day 4: User Authentication & JWT Security**
  - Implement password hashing using `bcrypt`.
  - Create registration (`/register`) and login (`/login`) API endpoints.
  - Implement JWT token generator and Bearer authentication dependency.
  - Secure protected test endpoints.

- [ ] **Day 5: Project Upload Pipeline & File Security**
  - Implement multipart ZIP upload endpoint (`/api/v1/projects/upload`).
  - Enforce file size limits (15 MB max).
  - Implement safe unzipping with Zip Slip prevention.
  - Create isolated user storage directories.

- [ ] **Day 6: Project Structure Validation**
  - Build validator service to verify required project layout:
    - Root containing `src/`, `tests/`, `requirements.txt`, `README.md`.
  - Implement clear, user-friendly validation error diagnostics.
  - Reject non-compliant archives safely.

- [ ] **Day 7: Project Static Analysis & Code Discovery**
  - Scan `src/` modules using Python's `ast` / file scanner.
  - Discover and catalog Pytest test files (`test_*.py`).
  - Extract discovered test function names and counts.
  - Store analysis summary in database.

---

### 📍 Week 2: Sandboxing, Pytest Execution & Result Parsing

- [ ] **Day 8: Docker Environment Setup & Base Image Creation**
  - Author a hardened, minimal `Dockerfile` for the test sandbox (Python 3.11 slim).
  - Pre-install `pytest` and essential test dependencies.
  - Build and tag base execution image (`testpilot-sandbox:latest`).

- [ ] **Day 9: Docker Sandbox Manager Service**
  - Implement backend Docker orchestration service using Docker SDK / CLI.
  - Configure container creation with security parameters:
    - `--network none`
    - `--memory 256m`
    - `--cpus 0.5`
    - `--read-only` mount of project files
    - Non-root user execution (`UID 1000`).

- [ ] **Day 10: Execution Supervision & Timeout Control**
  - Implement 30-second execution watchdog timer.
  - Handle container process termination and kill signals.
  - Implement automatic cleanup (`--rm`) to prevent orphaned containers and memory leaks.

- [ ] **Day 11: Pytest Test Runner Integration**
  - Trigger `pytest` execution inside the active container.
  - Configure Pytest output formatting (structured JSON report / JUnit XML).
  - Capture exit codes (0 = all passed, 1 = tests failed, 2 = execution error, etc.).

- [ ] **Day 12: Output Processing & Result Parsing**
  - Parse raw stdout, stderr, and JSON test reports.
  - Categorize individual test cases into: Passed, Failed, Skipped, Error.
  - Extract failure assertions, error messages, and line numbers.

- [ ] **Day 13: Database Persistence of Test Runs**
  - Store `TestRun` parent records (timestamp, duration, total counts).
  - Store granular `TestResult` items for each test case.
  - Link test runs to projects and authenticated users.

- [ ] **Day 14: Execution History & Query APIs**
  - Build API endpoints to retrieve past test runs (`/api/v1/projects/{id}/runs`).
  - Build endpoint to fetch granular results for a single run (`/api/v1/runs/{run_id}`).
  - Add pagination and historical trend metrics.

---

### 📍 Week 3: Frontend Dashboard, PDF Reporting & Final Evaluation

- [ ] **Day 15: Frontend Setup with Vite, React & Tailwind CSS**
  - Initialize React application using Vite and TypeScript.
  - Configure Tailwind CSS for modern styling.
  - Setup API client service (Axios / Fetch) and JWT auth state management.

- [ ] **Day 16: Authentication UI & Project Upload Dashboard**
  - Build modern Login and Register forms.
  - Create drag-and-drop ZIP upload component.
  - Display validation feedback and error alerts immediately.

- [ ] **Day 17: Interactive Test Runner & Results Console**
  - Build test execution trigger UI with loading spinners and status indicators.
  - Create expandable test case cards showing pass/fail status and stack traces.
  - Display summary metrics (Pass Rate %, Duration, Total Tests).

- [ ] **Day 18: Execution History View**
  - Build historical runs table showing previous attempts.
  - Enable comparing test outcomes across different uploads.

- [ ] **Day 19: PDF Report Generation Engine**
  - Implement ReportLab service in backend.
  - Design printable test certificate layout with tables, summary stats, and timestamps.
  - Build PDF download endpoint (`/api/v1/runs/{run_id}/report.pdf`).

- [ ] **Day 20: Security Hardening & Edge-Case Testing**
  - Test malicious uploads (Zip Slip, infinite loops, memory bombs, network socket attempts).
  - Verify container lockdown prevents unauthorized host access.
  - Conduct API input validation audits.

- [ ] **Day 21: Final Integration, Documentation & University Presentation Prep**
  - End-to-end user testing (Registration -> Upload -> Run -> View Results -> Download PDF).
  - Review documentation and clean up workspace.
  - Prepare demonstration script and architectural defense for university evaluators.
