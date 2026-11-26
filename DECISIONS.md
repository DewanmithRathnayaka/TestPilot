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

---

## ADR-011: Argon2id Password Hashing and Stateless JWT Authentication
- **Status:** Accepted (Day 5)
- **Context:** TestPilot must authenticate university students and evaluators without exposing user credentials or requiring complex server-side session stores.
- **Decision:**
  - Use `pwdlib` with the **Argon2id** algorithm for password hashing.
  - Issue cryptographically signed **JSON Web Tokens (JWT)** using the `HS256` HMAC-SHA256 algorithm.
  - Require the `Authorization: Bearer <token>` HTTP header for all protected endpoints.
- **Rationale:**
  - *Argon2id vs. MD5/SHA256:* Fast hash functions (MD5/SHA) can be brute-forced at billions of hashes per second on modern GPUs. Argon2id is memory-hard and time-hard, winning the Password Hashing Competition (PHC).
  - *Stateless JWT vs. Stateful Sessions:* JWT tokens carry the user identity inside the signed payload (`sub`). The server validates the signature mathematically without needing to query a Redis session store on every HTTP hop.
- **Consequences:** Highly scalable, stateless authentication. Token invalidation prior to expiration requires token blacklisting in production.

---

## ADR-012: Multi-Tenant Project Authorization via Foreign Key Ownership
- **Status:** Accepted (Day 5)
- **Context:** Multiple students and evaluators submit code on TestPilot. Student A must never be able to inspect, modify, or delete Student B's projects.
- **Decision:**
  - Add `user_id = Column(Integer, ForeignKey("users.id"))` to the `projects` table.
  - All project queries and mutations in `app/api/projects.py` are strictly scoped to `Project.user_id == current_user.id`.
  - Attempts to view or mutate another user's project by guessing the project ID immediately return `403 Forbidden`.
- **Consequences:** Strict multi-tenant data isolation; complete privacy between students.
