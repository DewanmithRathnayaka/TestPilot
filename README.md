# TestPilot – Automated Software Testing Platform

[![Project Status: Day 3 Complete](https://img.shields.io/badge/Status-Day%203%20REST%20APIs%20Complete-brightgreen.svg)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.12-brightgreen.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Vite-blue.svg)](#)
[![Sandbox](https://img.shields.io/badge/Execution-Docker%20Sandbox-orange.svg)](#)

## 📌 1. Project Overview
**TestPilot** is a web-based automated software testing platform designed for university students, educators, and software engineers. It enables users to upload Python projects as ZIP archives, validates project structures, executes test suites using **Pytest** inside isolated **Docker** containers, displays granular pass/fail analytics in real time, and exports publication-grade **PDF testing reports**.

---

## 🏗️ 2. Current Project Layout
```text
TestPilot/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              <-- FastAPI entrypoint & CORS middleware
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   └── routes.py        <-- API endpoints (/health, /info, /greeting, /test-message)
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── health.py        <-- Pydantic models for health and info
│   │   │   └── message.py       <-- Pydantic models with field length validation
│   │   └── core/
│   │       ├── __init__.py
│   │       └── config.py        <-- App configuration & CORS settings
│   ├── .venv/                   <-- Python virtual environment
│   ├── requirements.txt         <-- Python dependencies
│   ├── test_api.py              <-- Automated backend endpoint verification test suite
│   └── .env.example
│
├── frontend/
│   ├── src/
│   │   ├── App.tsx              <-- Interactive welcome dashboard & live backend monitor
│   │   ├── main.tsx             <-- React entrypoint
│   │   ├── config.ts            <-- Centralized API endpoint configuration
│   │   ├── index.css            <-- Clean dashboard styling
│   │   └── vite-env.d.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── .env
│
├── .gitignore                   <-- Git exclusions (venv, node_modules, temp files)
├── .env.example                 <-- Root global environment example
├── README.md                    <-- This documentation
├── REQUIREMENTS.md              <-- Functional (FR-01..11) & Non-Functional (NFR-01..17) Specs
├── ARCHITECTURE.md              <-- Architecture blueprints and Mermaid workflow
├── DEVELOPMENT_PROGRESS.md      <-- 21-Day milestone tracker
└── DECISIONS.md                 <-- Architectural Decision Records (ADR-001..009)
```

---

## ⚡ 3. How to Run TestPilot Locally

### Starting the Backend (FastAPI)
In a terminal:
```bash
# Navigate to backend and run with virtual environment Python
cd backend
.venv\Scripts\uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- API Base URL: `http://localhost:8000`
- Interactive Swagger Documentation: `http://localhost:8000/docs`
- Health Check: `http://localhost:8000/api/health`

### Starting the Frontend (React + Vite)
In a second terminal:
```bash
# Navigate to frontend and start Vite development server
cd frontend
npm run dev
```
- Frontend UI: `http://localhost:5173`

### Running the Backend Automated Test Suite
```bash
# Runs the automated endpoint and validation tests
python backend/test_api.py
```

---

## 📖 4. Documentation Index
- [REQUIREMENTS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/REQUIREMENTS.md): Functional and Non-Functional Requirements.
- [ARCHITECTURE.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/ARCHITECTURE.md): System architecture, sequence diagram, and security sandbox model.
- [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md): 21-Day progress tracker (Days 1–3 Complete).
- [DECISIONS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DECISIONS.md): Architectural Decision Records.
