# TestPilot – 21-Day Development Progress Tracker

This document tracks daily milestones, completed objectives, and upcoming phases across our 21-day development roadmap.

---

## 📅 Roadmap Overview

| Week | Focus Area | Status |
|---|---|---|
| **Week 1 (Days 1–7)** | Foundations, Architecture, Auth & Upload Pipeline | 🟡 In Progress (Days 1–3 Complete) |
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

- [x] **Day 2: Development Environment & Initial Project Setup**
  - Verified system environment: installed Python 3.12.10 and Node.js v26.13.1 (npm 11.20.0). Verified Git 2.55 and VS Code 1.147.
  - Created project directory structure: `backend/`, `frontend/`, `.gitignore`, `.env.example`.
  - Configured Python virtual environment (`backend/.venv`) and installed dependencies: `fastapi`, `uvicorn[standard]`, `pydantic`, `httpx`.
  - Created initial FastAPI application in `backend/app/main.py` with `GET /api/health` returning operational status JSON.
  - Configured CORS middleware for local frontend origins (`http://localhost:5173`).
  - Created React frontend with Vite & TypeScript in `frontend/`.
  - Created welcome UI displaying platform name, brand mark, subtitle, and dynamic backend connectivity status.
  - Successfully connected frontend to backend and verified error states when backend is down.

- [x] **Day 3: FastAPI Fundamentals & REST API Development**
  - Learned REST principles, HTTP methods (GET, POST, PUT, DELETE), JSON structures, path/query parameters, and HTTP status codes (200, 201, 400, 404, 422, 500).
  - Refactored backend into clean, modular structure:
    - `backend/app/core/config.py`: Centralized application settings and CORS policies.
    - `backend/app/schemas/health.py`: Pydantic models for health and application info responses.
    - `backend/app/schemas/message.py`: Pydantic request/response models with field length validation.
    - `backend/app/api/routes.py`: Modular API routing for all platform endpoints.
    - `backend/app/main.py`: Application entry point with router registration.
  - Implemented core REST endpoints:
    - `GET /api/health`: Health status check.
    - `GET /api/info`: Application name, version, and description.
    - `GET /api/`: Welcome endpoint with links to docs.
    - `POST /api/test-message`: Receives JSON payload with Pydantic validation (min/max length).
    - `GET /api/greeting`: Query parameter endpoint (`?name=...`).
    - `GET /api/items/{item_id}`: Error handling demonstrating custom `HTTPException(404)`.
  - Verified Swagger interactive documentation at `http://localhost:8000/docs`.
  - Built automated verification suite (`backend/test_api.py`) passing 8/8 tests.
  - Enhanced React frontend with real-time status card and interactive POST test form.

- [ ] **Day 4: Database Models & Migrations**
  - Design SQLAlchemy database schema (`User`, `Project`, `TestRun`, `TestResult`).
  - Setup SQLite database connection and session management.
  - Implement base CRUD helper functions.

- [ ] **Day 5: User Authentication & JWT Security**
  - Implement password hashing using `bcrypt`.
  - Create registration (`/register`) and login (`/login`) API endpoints.
  - Implement JWT token generator and Bearer authentication dependency.
  - Secure protected test endpoints.

- [ ] **Day 6: Project Upload Pipeline & File Security**
  - Implement multipart ZIP upload endpoint (`/api/v1/projects/upload`).
  - Enforce file size limits (15 MB max).
  - Implement safe unzipping with Zip Slip prevention.
  - Create isolated user storage directories.

- [ ] **Day 7: Project Structure Validation & Static Analysis**
  - Build validator service to verify required project layout (`src/`, `tests/`, etc.).
  - Scan `src/` modules and Pytest test functions using Python `ast`.
  - Display project diagnostics before execution.

---

### 📍 Week 2: Sandboxing, Pytest Execution & Result Parsing
*(Days 8–14: Docker sandbox creation, execution watchdog, Pytest parser, execution history APIs)*

---

### 📍 Week 3: Frontend Dashboard, PDF Reporting & Final Evaluation
*(Days 15–21: Dashboard UI, PDF reporting engine, security penetration tests, evaluator presentation)*
