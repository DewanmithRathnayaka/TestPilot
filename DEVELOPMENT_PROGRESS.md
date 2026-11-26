# TestPilot – 21-Day Development Progress Tracker

This document tracks daily milestones, completed objectives, and upcoming phases across our 21-day development roadmap.

---

## 📅 Roadmap Overview

| Week | Focus Area | Status |
|---|---|---|
| **Week 1 (Days 1–7)** | Foundations, Architecture, Auth, Database & Upload Pipeline | 🟡 In Progress (Days 1–5 Complete) |
| **Week 2 (Days 8–14)** | Docker Sandboxing, Pytest Engine & Result Processing | ⚪ Pending |
| **Week 3 (Days 15–21)** | Frontend Dashboard, PDF Reporting & Final Hardening | ⚪ Pending |

---

## 🚀 Daily Breakdown

### 📍 Week 1: Foundations, Architecture & Ingestion

- [x] **Day 1: Project Understanding, Requirements & System Architecture**
  - Clarified university project objectives and student learning goals.
  - Defined functional (FR-01 to FR-11) and non-functional requirements (NFR-01 to NFR-17).
  - Designed high-level client-server architecture with Docker sandbox model.
  - Authored foundational documentation: `README.md`, `REQUIREMENTS.md`, `ARCHITECTURE.md`, `DEVELOPMENT_PROGRESS.md`, `DECISIONS.md`.
  - Conducted 10-question fundamental knowledge check.

- [x] **Day 2: Development Environment & Initial Project Setup**
  - Verified system environment: installed Python 3.12.10 and Node.js v26.13.1 (npm 11.20.0). Verified Git 2.55 and VS Code 1.147.
  - Created project directory structure: `backend/`, `frontend/`, `.gitignore`, `.env.example`.
  - Configured Python virtual environment (`backend/.venv`) and installed dependencies: `fastapi`, `uvicorn[standard]`, `pydantic`, `httpx`.
  - Created initial FastAPI application with `GET /api/health` returning operational status JSON.
  - Configured CORS middleware for local frontend origins (`http://localhost:5173`).
  - Created React frontend with Vite & TypeScript in `frontend/`.
  - Created welcome UI displaying platform name, brand mark, and dynamic backend connectivity status.

- [x] **Day 3: FastAPI Fundamentals & REST API Development**
  - Mastered REST principles, HTTP methods, JSON structures, parameters, and HTTP status codes.
  - Refactored backend into clean, modular structure (`core/config.py`, `schemas/`, `api/routes.py`, `app/main.py`).
  - Implemented core REST endpoints: `/api/health`, `/api/info`, `/api/`, `/api/test-message` (validated POST), `/api/greeting`, and `/api/items/{id}` (404 handling).
  - Verified Swagger documentation at `/docs` and automated test suite (`backend/test_api.py`) passing 8/8 tests.

- [x] **Day 4: SQLite & SQLAlchemy Database Development**
  - Installed SQLAlchemy 2.1.9 in backend virtual environment.
  - Implemented database session management (`app/db/session.py`): engine, `SessionLocal`, declarative `Base`, and `get_db()` dependency.
  - Created SQLAlchemy ORM `Project` model (`app/models/project.py`) with columns: `id`, `name`, `description`, `language`, `status`, `created_at`.
  - Created Pydantic models (`app/schemas/project.py`): `ProjectCreate`, `ProjectUpdate`, and `ProjectResponse`.
  - Implemented complete CRUD REST endpoints (`app/api/projects.py`).
  - Built automated test suite (`backend/test_database.py`) passing 10/10 tests without regressions.

- [x] **Day 5: User Authentication & JWT Authorization**
  - Installed security dependencies: `pwdlib[argon2]`, `pyjwt`, `python-multipart`, `email-validator`.
  - Implemented cryptographic password hashing using Argon2id (`app/core/security.py`).
  - Implemented JWT token generation and verification using HMAC-SHA256 (`HS256`) with a 60-minute expiration window.
  - Created SQLAlchemy `User` model (`app/models/user.py`):
    - Table `users` with columns: `id` (PK), `username` (unique), `email` (unique), `hashed_password`, `created_at`.
    - One-to-many relationship with `projects` table (`cascade="all, delete-orphan"`).
  - Updated `Project` model with `user_id` foreign key referencing `users.id` and `owner` relationship.
  - Applied safe SQLite migration without data loss (`ALTER TABLE projects ADD COLUMN user_id INTEGER`).
  - Implemented Authentication API endpoints (`app/api/auth.py`):
    - `POST /api/auth/register`: Pydantic validation, duplicate checks, Argon2id hashing, returns 201 Created.
    - `POST /api/auth/login`: OAuth2 password form, verifies hash, issues JWT access token.
    - `GET /api/auth/me`: Protected endpoint returning user profile.
  - Created reusable FastAPI authentication dependency `get_current_user` (`app/api/deps.py`).
  - Enforced multi-tenant project authorization in `app/api/projects.py`:
    - Users can only create, list, view, update, and delete their own projects.
    - Unauthorized access attempts between different users strictly return `403 Forbidden`.
  - Built automated test suite `backend/test_auth.py` passing 19/19 tests. Full pipeline now passes 37/37 tests.
  - Connected React frontend: Login/Registration forms, JWT session handling, header user badge, sign out, and protected projects view.

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
