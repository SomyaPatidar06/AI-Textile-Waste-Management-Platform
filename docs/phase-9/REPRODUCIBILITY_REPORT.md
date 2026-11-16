# Phase 9 — Reproducibility & Environment Setup Guide

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Milestone:** Public GitHub Release Candidate  

---

## 1. System Requirements & Prerequisites

The platform has been validated on both Windows (PowerShell 5.1 / 7+) and Linux (Ubuntu 22.04 LTS / Debian 12):

- **Python:** Python 3.11, 3.12, or 3.14 (Virtual Environment recommended)
- **Node.js:** Node.js v18.x or v20.x (with npm v9+)
- **Database:** SQLite 3 (default for local dev) or PostgreSQL 16 (production)
- **RAM:** Minimum 4 GB RAM (8 GB recommended for simultaneous AI inference)
- **Disk:** Minimum 2 GB free disk space (excluding raw datasets)

---

## 2. Step-by-Step Clean Reproduction Protocol

### Step 1: Clone Repository
```bash
git clone https://github.com/SomyaPatidar06/AI-Textile-Waste-Management-Platform.git
cd AI-Textile-Waste-Management-Platform
```

### Step 2: Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.\.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install pinned dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Apply database migrations
alembic upgrade head

# Bootstrap initial test administrator and roles
python scripts/create_initial_admin.py
python scripts/seed_test_roles.py

# Start FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

### Step 3: Frontend Setup
```bash
cd ../frontend

# Install node dependencies
npm install

# Start Vite development server
npm run dev
```

The application will be live at:
- **Frontend UI:** `http://localhost:5173`
- **Backend API & Swagger Docs:** `http://127.0.0.1:8000/docs`

---

## 3. Reproducing Automated Test Suites

### 3.1 Backend Unit & Integration Tests (60 Tests)
```bash
cd backend
python -m pytest tests/ -v
```
*Expected Result:* 60 passed in ~145s.

### 3.2 End-to-End Acceptance Tests (17 Checkpoints)
```bash
cd backend
python scripts/phase8_acceptance_tests.py
```
*Expected Result:* 17 passed out of 17 checkpoints (100% success rate).

### 3.3 Independent AI Model Validation Suite
```bash
cd backend
python scripts/phase9_independent_ai_evaluation.py
```
*Expected Result:* Reproduces the 93.48% material accuracy, calibration ECE (0.0235), and ONNX 1.81x latency benchmark results.

### 3.4 Frontend Production Compilation
```bash
cd frontend
npm run build
```
*Expected Result:* Compiles cleanly into `dist/` with 0 warnings in ~4s.
