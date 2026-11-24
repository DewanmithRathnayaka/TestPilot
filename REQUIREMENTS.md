# TestPilot – Requirements Specification Document

This document defines the complete functional and non-functional requirements for the **TestPilot** Automated Software Testing Platform.

---

## 📋 1. Functional Requirements (FR)

Functional requirements describe the specific behavior, services, and features that the TestPilot system must provide.

### 👤 Module 1: User Management & Authentication
- **FR-01: User Registration**
  - The system shall allow new users to register an account using an email address, username, and password.
  - Passwords must be hashed using a cryptographically secure hashing algorithm (e.g., `bcrypt`) before storage in the database.
  - The system shall prevent duplicate registrations with identical usernames or emails.

- **FR-02: User Authentication & Session Management**
  - The system shall authenticate registered users by verifying their credentials and issuing a JSON Web Token (JWT).
  - All protected endpoints (uploads, test triggers, history, reports) shall require a valid Bearer JWT.
  - The system shall provide a secure logout mechanism that clears client-side credentials.

### 📦 Module 2: Project Upload & Validation
- **FR-03: Project Upload Handler**
  - The system shall provide an endpoint and UI interface allowing authenticated users to upload their code as a `.zip` archive.
  - The upload handler shall enforce a maximum file size limit (e.g., 15 MB) to prevent denial-of-service (DoS) storage exhaustion.
  - Uploaded files shall be assigned a unique Universally Unique Identifier (UUID) and stored in a designated, segregated working directory.

- **FR-04: Archive Structure Validation**
  - The system shall automatically inspect the contents of the uploaded `.zip` archive before extraction.
  - The system shall enforce the standardized project structure:
    - Root or nested project directory must contain `src/` and `tests/`.
    - Must contain `requirements.txt`.
    - Must contain `README.md`.
  - The system shall reject invalid archives with descriptive error messages (e.g., *"Missing required directory: tests/"*).
  - The system shall protect against "Zip Slip" vulnerabilities (preventing paths starting with `../` from escaping the extraction directory).

### 🔍 Module 3: Project Analysis
- **FR-05: Static Structure Analysis**
  - The system shall scan the validated `src/` directory and catalog Python modules (`.py` files), classes, and function definitions.
  - The system shall scan the `tests/` directory to identify test files adhering to the Pytest naming convention (`test_*.py` or `*_test.py`).
  - The system shall count total discovered test functions and display an overview in the project summary pane before execution.

### ⚙️ Module 4: Test Execution Engine & Sandboxing
- **FR-06: Sandbox Container Creation**
  - The system shall initialize an isolated, ephemeral Docker container based on a hardened lightweight Python image.
  - The project files shall be mounted into the container as read-only volumes (or copied into the disposable container layer).
  - The execution engine shall trigger `pytest` inside the container targeting the `/tests` folder.

- **FR-07: Test Output Capture & Parsing**
  - The system shall capture standard output (stdout), standard error (stderr), exit codes, and Pytest structured reports (JSON or JUnit XML).
  - The system shall parse and categorize test results into four discrete categories:
    - **Passed:** Tests that satisfied all assertions.
    - **Failed:** Tests where an assertion or logic condition failed.
    - **Skipped:** Tests explicitly marked to be skipped by decorators.
    - **Error:** Tests that encountered setup, teardown, syntax, or runtime exceptions.
  - Execution duration (seconds) and memory usage shall be recorded.

### 📊 Module 5: Test Results, History & Reporting
- **FR-08: Test Result Display Dashboard**
  - The React frontend shall present test run outcomes with visual indicators (green for pass, red for fail, yellow for skipped/error).
  - The user shall be able to expand each failed test case to view the traceback, expected vs. actual values, and code line location.

- **FR-09: Execution History**
  - The system shall record every test execution record in the database linked to the project and user.
  - Users shall be able to view past execution logs, date/time stamps, passing percentages, and historical progress.

- **FR-10: PDF Report Generation & Export**
  - The backend shall use ReportLab to dynamically generate a clean, branded PDF report for any completed test run.
  - The PDF shall contain:
    - Project metadata (Name, Author, Date, Execution ID).
    - Executive Summary (Total Tests, Pass Rate %, Execution Duration).
    - Detailed Breakdown table of individual test cases and failure reasons.
  - The user shall be able to download the generated PDF directly from the UI.

- **FR-11: Project Management**
  - Users shall be able to view a list of all their uploaded projects, view recent execution statuses, and delete projects (along with associated disk artifacts and database records).

---

## 🛡️ 2. Non-Functional Requirements (NFR)

Non-functional requirements specify the quality attributes, constraints, and security standards the system must meet.

### 🔒 Category 1: Security (Highest Priority)
- **NFR-01: Sandboxed Execution Isolation**
  - All uploaded user code MUST execute inside isolated Docker containers. No user code may run directly on the host operating system.
- **NFR-02: Zero Network Access**
  - Sandbox containers MUST have network access disabled (`--network none`). Uploaded code cannot communicate with external servers, databases, or local host services.
- **NFR-03: Resource Throttling**
  - Container resources MUST be strictly capped:
    - Maximum Memory: 256 MB per container.
    - Maximum CPU: 0.5 vCPU share.
  - Containers exceeding limits shall be killed immediately by the Docker daemon (OOM killer).
- **NFR-04: Strict Execution Timeouts**
  - Any test run exceeding 30 seconds MUST be aborted automatically to prevent infinite loops (`while True:`) or denial-of-service attempts.
- **NFR-05: Non-Root Execution**
  - Test processes inside the container MUST run under an unprivileged user (e.g., `UID 1000: sandboxuser`), not `root`.
- **NFR-06: Host Resource Protection & Cleanup**
  - Containers MUST be instantiated with `--rm` (or explicitly destroyed via backend API) to guarantee cleanup immediately after completion.
  - Temporary unpacked project folders must be stored in isolated directories and pruned upon job completion.

### ⚡ Category 2: Performance
- **NFR-07: Fast Validation Response**
  - Project structure validation and static analysis must complete within 2.0 seconds from the time of upload completion.
- **NFR-08: Container Cold-Start Optimization**
  - The Docker execution engine should utilize pre-built, cached base images to keep container initialization time under 1.5 seconds.
- **NFR-09: Light Client-Side Load**
  - The React frontend bundle should remain lightweight (< 500 KB compressed) and render interactive feedback within 100 milliseconds of user action.

### 🩺 Category 3: Reliability & Fault Tolerance
- **NFR-10: Graceful Failure Handling**
  - Malformed ZIP archives, corrupted test files, or crashing user scripts must never crash the FastAPI backend service.
  - The system must capture crashes and present user-friendly error messages.
- **NFR-11: Database Concurrency & Consistency**
  - Database writes for test runs and project records must execute inside atomic transactions to avoid orphaned records.

### 🎨 Category 4: Usability
- **NFR-12: Intuitive Student Experience**
  - The UI must clearly explain validation errors (e.g., indicating exactly which folder or file is missing) so undergraduate students can fix their project structure quickly.
- **NFR-13: Accessible Visual Indicators**
  - Color palettes for status indicators (passed, failed, pending) must include text labels and iconography for accessibility.

### 🧱 Category 5: Maintainability & Code Quality
- **NFR-14: Modular Separation of Concerns**
  - The architecture must separate the API routing, business logic, container orchestration, and database access layers into independent modules.
- **NFR-15: Strict Type Checking**
  - Both TypeScript (frontend) and Pydantic/Type Hints (backend) must enforce explicit data contracts to catch bugs during development.

### 📈 Category 6: Scalability & Portability
- **NFR-16: Independent Database Abstraction**
  - Database operations must be managed via SQLAlchemy ORM so that switching from SQLite (development) to PostgreSQL (production) requires only a configuration change.
- **NFR-17: Cross-Platform Consistency**
  - The application backend and container workflows must run consistently across Windows, macOS, and Linux developer environments.
