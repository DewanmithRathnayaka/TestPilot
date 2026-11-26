# TestPilot – Automated Software Testing Platform

[![Project Status: Day 5 Complete](https://img.shields.io/badge/Status-Day%205%20Auth%20%26%20JWT%20Complete-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.12-brightgreen.svg)](#)
[![Security](https://img.shields.io/badge/Security-Argon2id%20%7C%20JWT%20Bearer-blue.svg)](#)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20SQLAlchemy%202.1-blue.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-blue.svg)](#)

## 📌 1. Project Overview
**TestPilot** is a web-based automated software testing platform designed for university students, educators, and software engineers. It enables users to register, securely manage projects, upload ZIP archives, execute test suites using **Pytest** inside isolated **Docker** containers, inspect pass/fail analytics, and export publication-grade **PDF testing reports**.

---

## 🏗️ 2. Current Project Layout
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
│   │   │   └── project.py       <-- SQLAlchemy ORM model with user_id foreign key
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── health.py        <-- Pydantic schemas for health & info
│   │   │   ├── message.py       <-- Pydantic schemas for test messages
│   │   │   ├── project.py       <-- Pydantic schemas for Project CRUD
│   │   │   └── user.py          <-- Pydantic schemas for Registration, Login, Token, Profile
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── deps.py          <-- get_current_user OAuth2 Bearer security dependency
│   │       ├── routes.py        <-- General endpoints (/health, /info, /greeting)
│   │       ├── auth.py          <-- Authentication endpoints (/register, /login, /me)
│   │       └── projects.py      <-- Multi-tenant authorized project CRUD endpoints
│   ├── .venv/                   <-- Isolated Python 3.12 virtual environment
│   ├── requirements.txt         <-- Python dependencies
│   ├── test_api.py              <-- Day 3 test suite (8 tests)
│   ├── test_database.py         <-- Day 4 database test suite (10 tests)
│   ├── test_auth.py             <-- Day 5 authentication & authorization test suite (19 tests)
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              <-- Dashboard with JWT login/register & authorized projects
│   │   ├── main.tsx             <-- React entrypoint
│   │   ├── config.ts            <-- Centralized API endpoint URLs
│   │   ├── index.css            <-- Polished dark-mode developer styling
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
│
├── testpilot.db                 <-- Local SQLite database (users & projects tables)
├── .gitignore                   <-- Clean version control exclusions
├── .env.example                 <-- Global environment template
├── README.md                    <-- This documentation
├── REQUIREMENTS.md              <-- Functional (FR-01..11) & Non-Functional (NFR-01..17) Specs
├── ARCHITECTURE.md              <-- Architecture blueprints and Mermaid workflow
├── DEVELOPMENT_PROGRESS.md      <-- 21-Day milestone tracker (Days 1–5 Complete)
└── DECISIONS.md                 <-- Architectural Decision Records (ADR-001..012)
```

---

## ⚡ 3. How to Run TestPilot Locally

### Starting the Backend (FastAPI + SQLite + JWT)
In terminal 1:
```bash
# Navigate to backend and run with virtual environment Python
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Registration: `POST /api/auth/register`
- Login: `POST /api/auth/login`
- Current User Profile: `GET /api/auth/me`

### Starting the Frontend (React + Vite)
In terminal 2:
```bash
# Navigate to frontend and start Vite development server
cd frontend
npm run dev
```
- Frontend Dashboard: `http://localhost:5173`

### Running the Full Automated Test Pipeline (37 Tests)
```bash
python backend/test_api.py
python backend/test_database.py
python backend/test_auth.py
```

---

## 📖 4. Documentation Index
- [REQUIREMENTS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/REQUIREMENTS.md): Functional and Non-Functional Requirements.
- [ARCHITECTURE.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/ARCHITECTURE.md): System architecture, sequence diagram, and security sandbox model.
- [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md): 21-Day progress tracker (Days 1–5 Complete).
- [DECISIONS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DECISIONS.md): Architectural Decision Records (ADRs 001–012).
