# Phase 8 — Deployment Rehearsal & Container Orchestration

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Deployment Profile:** Docker Compose Multi-Container Stack (Nginx + FastAPI + PostgreSQL 16)  

---

## 1. Container Architecture Overview

The platform is fully containerized into three decoupled microservices:

```
[ Client Browser ]
        │
        ▼ (Port 80)
┌────────────────────────────────────────────────────────┐
│  frontend (Nginx 1.25-alpine)                          │
│  - Serves compiled Vite SPA assets (HTML/CSS/JS)       │
│  - Enforces security headers & gzip compression        │
│  - Reverse-proxies /api/ requests to backend container │
│  - Responds to /health probe                           │
└────────────────────────────────────────────────────────┘
        │
        ▼ (Port 8000 via internal docker network)
┌────────────────────────────────────────────────────────┐
│  backend (FastAPI / Uvicorn Python 3.11/3.14)          │
│  - AI Inference Pipelines (ResNet-18, ONNX Runtime)   │
│  - Business logic, Circularity formulas, LCA Engine    │
│  - Liveness & Readiness health endpoints               │
│  - Persistent uploads volume (/app/uploads)            │
└────────────────────────────────────────────────────────┘
        │
        ▼ (Port 5432 via internal docker network)
┌────────────────────────────────────────────────────────┐
│  postgres (PostgreSQL 16-alpine)                       │
│  - ACID relational storage for inventory and analyses  │
│  - Persistent data volume (postgres_data)              │
│  - Docker healthcheck via pg_isready                   │
└────────────────────────────────────────────────────────┘
```

---

## 2. Service Definitions & Health Probes

### 2.1 Backend Service
- **Dockerfile:** `backend/Dockerfile`
  - Multi-stage build based on `python:3.11-slim` or `python:3.14`.
  - Non-root application user execution.
  - Pre-installed PyTorch CPU, torchvision, ONNX Runtime, and FastAPI.
- **Healthcheck Configuration:**
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://127.0.0.1:8000/health/live || exit 1"]
    interval: 15s
    timeout: 5s
    retries: 3
    start_period: 15s
  ```
- **Readiness Probe:**
  - Evaluates database connectivity (`SELECT 1`), upload directory writeability, and model checkpoint presence (`fabric_model_v2.pth` / ONNX and `aitex_defect_model.pth` / ONNX).
  - Endpoint: `GET /health/ready` (and alias `GET /api/v1/health/ready`).

### 2.2 Frontend Service
- **Dockerfile:** `frontend/Dockerfile`
  - Multi-stage build: Stage 1 compiles React assets via `npm run build`; Stage 2 copies output to `nginx:alpine`.
- **Nginx Reverse Proxy:**
  - Routes `/api/` traffic to `http://backend:8000/api/`.
  - Serves Single Page Application routes with `try_files $uri $uri/ /index.html;`.
- **Healthcheck Configuration:**
  ```yaml
  healthcheck:
    test: ["CMD-SHELL", "curl -f http://127.0.0.1/health || exit 1"]
    interval: 15s
    timeout: 5s
    retries: 3
  ```

### 2.3 PostgreSQL Database Service
- **Image:** `postgres:16-alpine`
- **Volume:** `postgres_data` persistent named volume.
- **Healthcheck:** `pg_isready -U ${POSTGRES_USER} -d ${POSTGRES_DB}`.

---

## 3. Database Migration & Dual-Engine Capability

The application supports seamless operation under dual database engines:
1. **SQLite (Development & Air-Gapped Field Testing):**
   - Configured via `DATABASE_URL="sqlite:///./textile_waste.db"`.
   - Enabled with zero-lock online backup via `scripts/backup_database.py`.
2. **PostgreSQL (Production & Multi-Node Cluster):**
   - Configured via standard SQLAlchemy PostgreSQL connection strings.
   - Fully supported by Alembic migration revisions:
     - `883b186bad06`: Initial schema (users, batches, status_history, analyses, notifications).
     - `f703a183dc31`: Bounding boxes column addition.
     - `59a79ed71fbf`: Circularity scoring breakdown and extended role enums.

---

## 4. Disaster Recovery & Zero-Lock Backup Rehearsal

A dry-run database backup was executed on the live SQLite database:
- **Command:** `python backend/scripts/backup_database.py`
- **Output:**
  ```
  Creating SQLite backup to backups/textile_waste_backup_20261116_110940.db...
  Backup successful! Verified integrity: 'ok'. Size: 0.16 MB
  ```
- **Verification:** The backup file was opened in read-only mode, and `PRAGMA integrity_check` verified zero corruption.

---

## 5. Deployment Commands Quick Reference

### Starting the Production Stack
```bash
# 1. Copy and configure production secrets
cp .env.example .env

# 2. Build and launch all containers in detached mode
docker compose up -d --build

# 3. Check health and running status
docker compose ps

# 4. View unified logs
docker compose logs -f
```

### Applying Alembic Migrations inside Container
```bash
docker compose exec backend alembic upgrade head
```

### Seeding Default Administrator
```bash
docker compose exec backend python scripts/create_initial_admin.py
```
