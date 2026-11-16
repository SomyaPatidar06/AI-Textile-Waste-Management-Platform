# Local Execution & Developer Run Guide

**Project:** AI Textile Waste Management Platform  
**Target:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Version:** 2.0.0  

---

## 1. Prerequisites

Before starting, ensure you have the following installed on your machine:

- **Python:** 3.12+ (tested and verified on Python 3.14.0)
- **Node.js:** 18+ (tested and verified on Node.js v24.12.0)
- **Package Managers:** `pip` and `npm` (npm 10+ / 11+)
- **Operating System:** Windows 10/11, macOS, or Linux

---

## 2. Quickstart (One-Click Launchers)

Two automated PowerShell scripts are provided in the repository root to start the backend and frontend independently:

### Terminal 1: Backend
```powershell
.\start-backend.ps1
```
*Automatically runs Alembic migrations, bootstraps the default administrator account, and starts Uvicorn on `http://127.0.0.1:8000`.*

### Terminal 2: Frontend
```powershell
.\start-frontend.ps1
```
*Installs npm packages if needed and launches the Vite development server on `http://localhost:5173` with automated API proxying.*

---

## 3. Manual Step-by-Step Setup

If you prefer running manual commands or are running on macOS/Linux:

### Step 3.1 — Backend Configuration & Startup

```bash
# 1. Navigate to backend directory
cd backend

# 2. (Optional) Create and activate virtual environment
python -m venv venv
# Windows (PowerShell):
.\venv\Scripts\Activate.ps1
# Linux / macOS:
source venv/bin/activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment (optional - defaults work out of the box)
cp .env.example .env

# 5. Run database migrations (creates SQLite tables with Alembic)
python -m alembic upgrade head

# 6. Seed the initial administrator account
python scripts/create_initial_admin.py

# 7. Start the FastAPI development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

- **Backend Health Check:** `http://127.0.0.1:8000/health`
- **Interactive Swagger Documentation:** `http://127.0.0.1:8000/docs`

---

### Step 3.2 — Frontend Configuration & Startup

```bash
# 1. Open a new terminal and navigate to frontend directory
cd frontend

# 2. Install Node dependencies
npm install

# 3. Start the Vite development server
npm run dev
```

- **Frontend Application UI:** `http://localhost:5173`

---

## 4. Default Seed Credentials

Upon running `create_initial_admin.py`, the following initial administrator is available:

| Attribute | Credential |
|---|---|
| **Role** | `ADMIN` |
| **Username** | `admin` |
| **Email** | `admin@textilewaste.platform` |
| **Password** | `AdminSecret2026!` |

*You can also self-register new `OPERATOR`, `RECYCLER`, or `VIEWER` accounts directly from the UI registration page at `http://localhost:5173/register`.*

---

## 5. Automated Verification & Testing

To run the complete automated test suite:

```powershell
# Run backend regression tests (41 tests)
python -m pytest backend/tests -v

# Run end-to-end manual QA workflow audit script
python backend/scripts/manual_qa_verification.py

# Build frontend production bundle
npm run build --prefix frontend
```

---

## 6. Troubleshooting Common Startup Issues

### 1. `Address already in use` (Port 8000 or 5173)
- **Cause:** Another process is already running on port 8000 or 5173.
- **Fix:**
  ```powershell
  # Find PID using port 8000:
  Get-NetTCPConnection -LocalPort 8000 | Select-Object OwningProcess
  # Terminate process:
  Stop-Process -Id <PID> -Force
  ```

### 2. `ModuleNotFoundError: No module named 'app'`
- **Cause:** Running uvicorn outside the `backend/` directory without setting `PYTHONPATH`.
- **Fix:** Either `cd backend` first or set `$env:PYTHONPATH="backend"` before launching.

### 3. Frontend Cannot Reach Backend (Network Error)
- **Cause:** Backend server is not running on `http://127.0.0.1:8000`.
- **Fix:** Ensure the backend terminal is active and accessible at `http://127.0.0.1:8000/health`. Vite's proxy automatically routes `/api` to `http://127.0.0.1:8000`.

### 4. Database Schema Out of Sync
- **Cause:** Database file was created before latest migrations.
- **Fix:**
  ```powershell
  cd backend
  python -m alembic upgrade head
  ```
