# TestPilot – Automated Software Testing Platform

[![Project Status: Day 1 - Architecture & Requirements](https://img.shields.io/badge/Status-Day%201%20Planning%20%26%20Design-blue.svg)](#)
[![Python](https://img.shields.io/badge/Backend-FastAPI%20%7C%20Python%203.11+-brightgreen.svg)](#)
[![Frontend](https://img.shields.io/badge/Frontend-React%20%7C%20TypeScript%20%7C%20Tailwind-blue.svg)](#)
[![Sandbox](https://img.shields.io/badge/Execution-Docker%20Sandbox-orange.svg)](#)

## 📌 1. Project Overview
**TestPilot** is a web-based automated software testing platform designed for developers, educators, and students. It allows users to upload standard Python projects as compressed ZIP archives, safely unpack and validate them, run automated test suites with **Pytest** inside isolated **Docker** sandbox containers, inspect real-time pass/fail metrics, and download clean audit-ready **PDF testing reports**.

---

## 🎯 2. Problem Statement
Evaluating student programming assignments and testing developer code manually has major drawbacks:
1. **Security Vulnerability:** Executing untrusted code directly on a university server or personal machine exposes the host system to accidental deletions (`rm -rf /` or `os.remove`), infinite resource loops (fork bombs, CPU freezing), or malicious network socket connections.
2. **Environment Inconsistency:** Code that runs on a student's machine often fails on an evaluator's machine ("it works on my machine" syndrome) due to missing packages or mismatched OS libraries.
3. **Manual Overhead:** Unzipping, configuring virtual environments, running test commands, and recording scores manually wastes hours of instructor and developer time.

**TestPilot solves this** by providing a unified web dashboard, an automated standardized pipeline, and a hardened containerized sandbox where code runs safely and yields reproducible test reports.

---

## 🚀 3. Core Features
- **User Authentication:** Secure JWT-based registration and login system.
- **ZIP Project Upload & Validation:** Ensures submitted archives match standardized layout standards.
- **Code & Test Structure Analysis:** Scans test signatures and production modules before execution.
- **Hardened Docker Sandboxing:** Ephemeral container isolation with zero network access, memory caps, CPU caps, and strict execution timeouts.
- **Pytest Test Runner Integration:** Parses Pytest JSON/JUnit output into clear passed, failed, skipped, and error classifications.
- **Execution History:** Maintains historical audit logs of test runs per project with timestamps and metrics.
- **PDF Report Generation:** Generates downloadable testing certificates and executive summaries powered by ReportLab.

---

## 🛠️ 4. Technology Stack & Justification

| Layer | Technology | Reason for Choice |
|---|---|---|
| **Frontend Framework** | React 18 + Vite | Blazing fast build tooling, reactive UI updates for test progress, and rich component ecosystem. |
| **Language (Frontend)** | TypeScript | Catches type mismatch errors at compile time, improving code maintainability. |
| **Styling** | Tailwind CSS | Utility-first CSS for clean, consistent developer dashboards without bulky custom CSS sheets. |
| **Backend Framework** | Python & FastAPI | High-performance asynchronous API framework, automatic OpenAPI documentation, and native Python ecosystem integration. |
| **Data Validation** | Pydantic | Robust input data validation and serialization using Python type hints. |
| **ORM / Database Access**| SQLAlchemy | Industry-standard Object-Relational Mapper that cleanly abstracts SQL queries. |
| **Database** | SQLite | Lightweight, zero-configuration relational database ideal for development and single-node deployment. |
| **Execution Sandbox** | Docker | Complete OS-level container isolation preventing untrusted student code from harming the host server. |
| **Test Runner** | Pytest | De facto Python test framework with rich plugin ecosystem, fixture support, and structured output. |
| **Report Generation** | ReportLab | Production-grade programmatic PDF engine capable of rendering tables, summaries, and styling. |
| **Tooling & IDE** | Git, GitHub & Antigravity IDE | Source control tracking and intelligent AI-assisted software development environment. |

---

## 📁 5. Expected Project Directory Layout for Uploads
All uploaded projects must conform to the following convention:
```text
project_name/
├── src/
│   └── (application source code .py files)
├── tests/
│   └── (pytest test cases named test_*.py)
├── requirements.txt
└── README.md
```

---

## 🗺️ 6. 21-Day Development Plan Summary
- **Week 1 (Days 1–7):** Requirements, Architecture, Project Setup, Authentication, and Project Upload Pipeline.
- **Week 2 (Days 8–14):** Docker Sandbox Isolation, Pytest Engine Integration, and Execution Result Processing.
- **Week 3 (Days 15–21):** Frontend Dashboard, PDF Reporting Engine, Security Hardening, and Final Evaluation.

For a complete breakdown, refer to [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md).

---

## 📖 7. Project Documentation Index
- [REQUIREMENTS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/REQUIREMENTS.md): Comprehensive Functional & Non-Functional Requirements.
- [ARCHITECTURE.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/ARCHITECTURE.md): System Architecture, Component Communication, and Security Model.
- [DECISIONS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DECISIONS.md): Architectural Decision Records (ADRs).
- [DEVELOPMENT_PROGRESS.md](file:///c:/Users/chanu/OneDrive/Desktop/new%20Testpilot/DEVELOPMENT_PROGRESS.md): Day-by-day milestone tracker.
