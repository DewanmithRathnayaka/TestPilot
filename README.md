# TestPilot – Automated Software Testing Platform

[![Project Status: Day 4 Complete](https://img.shields.io/badge/Status-Day%204%20SQLite%20%26%20SQLAlchemy%20Complete-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.12-brightgreen.svg)](#)
[![Database](https://img.shields.io/badge/Database-SQLite%20%7C%20SQLAlchemy%202.1-blue.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-blue.svg)](#)

## 📌 1. Project Overview
**TestPilot** is a web-based automated software testing platform designed for university students, educators, and software engineers. It enables users to register projects, validates project structures, executes test suites using **Pytest** inside isolated **Docker** containers, displays granular pass/fail analytics in real time, and exports publication-grade **PDF testing reports**.

---

## 🏗️ 2. Current Project Layout
```text
TestPilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              <-- FastAPI entrypoint, table creation, CORS & router mount
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   └── config.py        <-- Centralized settings (DB URL, CORS, project info)
│   │   ├── db/
│   │   │   ├── __init__.py
│   │   │   └── session.py       <-- Engine, SessionLocal, declarative Base & get_db dependency
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── project.py       <-- SQLAlchemy ORM model for 'projects' table
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── health.py        <-- Pydantic schemas for health & info
│   │   │   ├── message.py       <-- Pydantic schemas for test messages
│   │   │   └── project.py       <-- Pydantic schemas for Project CRUD (Create, Update, Response)
│   │   └── api/
│   │       ├── __init__.py
│   │       ├── routes.py        <-- General endpoints (/health, /info, /greeting)
│   │       └── projects.py      <-- Project CRUD endpoints (/api/projects)
│   ├── .venv/                   <-- Isolated Python 3.12 virtual environment
│   ├── requirements.txt         <-- Python dependencies (FastAPI, SQLAlchemy, Uvicorn, Pydantic)
│   ├── test_api.py              <-- Day 3 test suite
│   ├── test_database.py         <-- Day 4 automated database & CRUD test suite
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              <-- Dashboard with real-time SQLite Project CRUD UI
│   │   ├── main.tsx             <-- React entrypoint
│   │   ├── config.ts            <-- Centralized API endpoint URLs
│   │   ├── index.css            <-- Dark-mode developer dashboard styling
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
│
├── testpilot.db                 <-- Local SQLite database file (persistent storage)
├── .gitignore                   <-- Clean version control exclusions
├── .env.example                 <-- Global environment template
├── README.md                    <-- This documentation
├── REQUIREMENTS.md              <-- Functional (FR-01..11) & Non-Functional (NFR-01..17) Specs
├── ARCHITECTURE.md              <-- Architecture blueprints and Mermaid workflow
├── DEVELOPMENT_PROGRESS.md      <-- 21-Day milestone tracker (Days 1–4 Complete)
└── DECISIONS.md                 <-- Architectural Decision Records (ADR-001..010)
```

---

## ⚡ 3. How to Run TestPilot Locally

### Starting the Backend (FastAPI + SQLite)
In terminal 1:
```bash
# Navigate to backend and run with virtual environment Python
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`
- Projects Endpoint: `http://localhost:8000/api/projects`

### Starting the Frontend (React + Vite)
In terminal 2:
```bash
# Navigate to frontend and start Vite development server
cd frontend
npm run dev
```
- Frontend Dashboard: `http://localhost:5173`

### Running the Automated Test Suites
```bash
# Verify Day 3 general endpoints
python backend/test_api.py

# Verify Day 4 SQLite database and CRUD operations
python backend/test_database.py
```

---

## 📖 4. Documentation Index
- [REQUIREMENTS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/REQUIREMENTS.md): Functional and Non-Functional Requirements.
- [ARCHITECTURE.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/ARCHITECTURE.md): System architecture, sequence diagram, and security sandbox model.
- [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md): 21-Day progress tracker (Days 1–4 Complete).
- [DECISIONS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DECISIONS.md): Architectural Decision Records.
