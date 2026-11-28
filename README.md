# TestPilot – Automated Software Testing Platform

[![Project Status: Day 7 Complete](https://img.shields.io/badge/Status-Day%207%20Static%20AST%20Analysis%20Complete-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.12-brightgreen.svg)](#)
[![Security](https://img.shields.io/badge/Security-Zip%20Slip%20Guard%20%7C%20Argon2id%20%7C%20JWT%20%7C%20Pure%20Static%20AST-blue.svg)](#)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20SQLAlchemy%202.1-blue.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-blue.svg)](#)

## 📌 1. Project Overview
**TestPilot** is a web-based automated software testing platform designed for university students, educators, and software engineers. It enables users to register, securely manage projects, upload ZIP archives, execute test suites using **Pytest** inside isolated **Docker** containers, inspect pass/fail analytics, and export publication-grade **PDF testing reports**.

---

## 📁 2. Supported Project Structure
All uploaded archives must conform to the standard Pytest layout:
```text
project_name/
├── src/
│   ├── main.py
│   └── calculator.py
├── tests/
│   ├── test_main.py
│   └── test_calculator.py
├── requirements.txt
└── README.md
```

---

## 🏗️ 3. Current Project Layout
```text
TestPilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              <-- FastAPI entrypoint, safe migration, CORS & router registration
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── config.py        <-- Settings (DB URL, JWT Secret, CORS origins)
│   │   │   └── security.py      <-- Argon2id password hashing & JWT token issuance/decoding
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── session.py       <-- Engine, SessionLocal, Base & get_db dependency
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── user.py          <-- SQLAlchemy ORM model for 'users' table
│   │   │   └── project.py       <-- SQLAlchemy ORM model with upload metadata and user_id FK
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── health.py        <-- Pydantic schemas for health & info
│   │   │   ├── message.py       <-- Pydantic schemas for test messages
│   │   │   ├── project.py       <-- Pydantic schemas for Project CRUD & Upload
│   │   │   ├── user.py          <-- Pydantic schemas for Registration, Login, Token, Profile
│   │   │   └── analysis.py      <-- Pydantic schemas for Static AST Analysis & Pytest Candidates
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── upload_service.py<-- Secure ZIP upload, Zip Slip defense, and static validation
│   │   │   └── project_analyzer.py <-- AST parser, Pytest candidate discovery, requirements check
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── deps.py          <-- get_current_user OAuth2 Bearer security dependency
│   │       ├── routes.py        <-- General endpoints (/health, /info, /greeting)
│   │       ├── auth.py          <-- Authentication endpoints (/register, /login, /me)
│   │       └── projects.py      <-- Authorized project CRUD, /upload and /{id}/analyze endpoints
│   ├── .venv/                   <-- Isolated Python 3.12 virtual environment
│   ├── requirements.txt         <-- Python dependencies
│   ├── test_api.py              <-- Day 3 test suite (8 tests)
│   ├── test_database.py         <-- Day 4 database test suite (10 tests)
│   ├── test_auth.py             <-- Day 5 authentication test suite (19 tests)
│   ├── test_upload.py           <-- Day 6 secure upload test suite (17 tests)
│   ├── test_analysis.py         <-- Day 7 AST static analysis test suite (29 tests)
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              <-- Dashboard with JWT auth, ZIP upload & AST Analysis Modal
│   │   ├── main.tsx             <-- React entrypoint
│   │   ├── config.ts            <-- Centralized API endpoint URLs
│   │   ├── index.css            <-- Polished dark-mode developer styling with Modal
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
│
├── uploads/                     <-- Secure internal project storage (ignored by Git)
├── testpilot.db                 <-- Local SQLite database (users & projects tables)
├── .gitignore                   <-- Clean version control exclusions
├── .env.example                 <-- Global environment template
├── README.md                    <-- This documentation
├── REQUIREMENTS.md              <-- Functional (FR-01..11) & Non-Functional (NFR-01..17) Specs
├── ARCHITECTURE.md              <-- Architecture blueprints and Mermaid workflow
├── DEVELOPMENT_PROGRESS.md      <-- 21-Day milestone tracker (Days 1–7 Complete)
└── DECISIONS.md                 <-- Architectural Decision Records (ADRs 001–014)
```

---

## ⚡ 4. How to Run TestPilot Locally

### Starting the Backend (FastAPI + SQLite + Upload & Analysis Service)
In terminal 1:
```bash
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- ZIP Upload Endpoint: `POST /api/projects/upload`
- AST Analysis Endpoint: `POST /api/projects/{id}/analyze`

### Starting the Frontend (React + Vite)
In terminal 2:
```bash
cd frontend
npm run dev
```
- Frontend Dashboard: `http://localhost:5173`

### Running the Full Automated Test Pipeline (83 Tests)
```bash
python backend/test_api.py
python backend/test_database.py
python backend/test_auth.py
python backend/test_upload.py
python backend/test_analysis.py
```

---

## 📖 5. Documentation Index
- [REQUIREMENTS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/REQUIREMENTS.md): Functional and Non-Functional Requirements.
- [ARCHITECTURE.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/ARCHITECTURE.md): System architecture, sequence diagram, and security sandbox model.
- [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md): 21-Day progress tracker (Days 1–7 Complete).
- [DECISIONS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DECISIONS.md): Architectural Decision Records (ADRs 001–014).
