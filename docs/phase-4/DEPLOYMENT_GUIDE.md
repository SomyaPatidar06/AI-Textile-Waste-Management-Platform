# Platform Deployment & Operations Guide

**Target Platform:** AI Textile Waste Management Platform v2.1.0  
**Phase:** 4.5 — Containerization & Deployment  
**Date:** November 15, 2026  
**Audience:** DevOps Engineers, Platform Administrators, and Developers  

---

## 1. Overview & Deployment Topologies

The AI Textile Waste Management Platform supports two primary deployment topologies:
1. **Containerized Production Stack (Recommended for Production):**
   - Multi-container orchestration using `docker-compose.yml`.
   - Dedicated PostgreSQL 16 relational database with persistent named volumes and healthcheck dependencies.
   - High-performance Nginx reverse proxy serving the compiled React SPA and routing API traffic to the backend.
   - Hardened FastAPI backend executing under a non-root system user (`appuser`).
2. **Local Development Mode (Rapid Prototyping):**
   - Standalone Windows / Linux execution using Python virtual environments and Vite development server.
   - Zero-dependency embedded SQLite database (`textile_waste.db`).

---

## 2. Environment Configuration

Copy the sample environment file to `.env` in the project root:

```bash
cp .env.example .env
```

### Key Environment Variables

| Variable | Description | Recommended Value (Production) | Default (Development) |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | SQLAlchemy connection string | `postgresql://postgres:postgres@db:5432/textile_db` | `sqlite:///./textile_waste.db` |
| `SECRET_KEY` | JWT signing secret | Secure random 64-character hex string | Development fallback |
| `ALGORITHM` | JWT cryptographic algorithm | `HS256` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Access token lifespan | `30` | `30` |
| `REFRESH_TOKEN_EXPIRE_DAYS` | Refresh token lifespan | `7` | `7` |
| `POSTGRES_DB` | PostgreSQL database name | `textile_db` | `textile_db` |
| `POSTGRES_USER` | PostgreSQL superuser | `postgres` | `postgres` |
| `POSTGRES_PASSWORD` | PostgreSQL password | Strong custom password | `postgres` |
| `DB_POOL_SIZE` | Database connection pool capacity | `10` | `5` |
| `DB_MAX_OVERFLOW` | Maximum surge pool connections | `20` | `10` |
| `MAX_FILE_SIZE_BYTES` | Maximum upload size (bytes) | `10485760` (10 MB) | `10485760` |

---

## 3. Containerized Deployment (Docker Compose)

### 3.1 Prerequisites
- Docker Engine 24.0+ and Docker Compose v2.20+
- 4 GB available system RAM
- 10 GB available disk space

### 3.2 Starting the Stack

From the root repository directory:

```bash
# Build images and start all containers in detached mode
docker compose up --build -d
```

### 3.3 Verifying Service Health

Docker Compose orchestrates three interconnected services:

```bash
docker compose ps
```

Expected output:
```
NAME                                   IMAGE               COMMAND                  SERVICE    STATUS
ai-textile-platform-db-1               postgres:16-alpine  "docker-entrypoint.s…"   db         Up (healthy)
ai-textile-platform-backend-1          backend:latest      "uvicorn app.main:ap…"   backend    Up (healthy)
ai-textile-platform-frontend-1         frontend:latest     "/docker-entrypoint.…"   frontend   Up (healthy)
```

### 3.4 Container Architecture Details
- **`db`:** PostgreSQL 16 Alpine with healthcheck running `pg_isready -U postgres`. Persistent data stored in `postgres_data` volume.
- **`backend`:** Multi-stage Python 3.11 build. Non-root user (`appuser`), internal port 8000. Depends on `db` being `healthy`. Healthcheck queries `/health/ready`.
- **`frontend`:** Multi-stage Node 18 build compiled via Vite into static assets served by Alpine Nginx on port 80. Routes `/api/*` and `/uploads/*` directly to `http://backend:8000`.

### 3.5 Stopping the Stack

```bash
docker compose down
```
To purge database volumes (Caution: destructive action):
```bash
docker compose down -v
```

---

## 4. Local Development Startup (Windows PowerShell)

For development without Docker:

### 4.1 Backend Service

```powershell
# Navigate to backend
cd D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend

# Activate virtual environment
.\.venv\Scripts\Activate.ps1

# Start Uvicorn development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The API will be available at `http://127.0.0.1:8000` with interactive OpenAPI docs at `http://127.0.0.1:8000/docs`.

### 4.2 Frontend Service

In a separate terminal:

```powershell
# Navigate to frontend
cd D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\frontend

# Install dependencies (if needed)
npm install

# Start Vite dev server
npm run dev
```

The application will launch at `http://localhost:5173/`.

---

## 5. Database Backup & Disaster Recovery

The platform includes an automated zero-lock hot backup utility for SQLite deployments. It utilizes the native SQLite online backup API to copy pages incrementally while concurrent reads and writes proceed uninterrupted.

### 5.1 Performing a Backup

```powershell
cd D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend
.\.venv\Scripts\python.exe scripts/backup_database.py --verify
```

Output:
```
2026-11-15 15:08:25 [INFO] Starting zero-lock SQLite online backup...
2026-11-15 15:08:25 [INFO] Source database: D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend\textile_waste.db
2026-11-15 15:08:25 [INFO] Target backup:   D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend\backups\textile_waste_backup_20261115_150825.db
2026-11-15 15:08:25 [INFO] Backup completed successfully.
2026-11-15 15:08:25 [INFO] Verifying database integrity (PRAGMA integrity_check)...
2026-11-15 15:08:25 [INFO] Database integrity check PASSED (ok). File size: 147456 bytes.
```

### 5.2 Scheduled Cron / Windows Task
To schedule nightly backups at 02:00:
- **Windows Task Scheduler:** Trigger action `powershell -ExecutionPolicy Bypass -File D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend\scripts\backup_database.ps1`.
- **Linux Crontab:** `0 2 * * * /opt/platform/backend/.venv/bin/python /opt/platform/backend/scripts/backup_database.py --verify >> /var/log/backup.log 2>&1`.

### 5.3 Restoring from Backup

1. Stop the backend service:
   ```powershell
   # Stop uvicorn process
   ```
2. Archive the corrupt/damaged database file:
   ```powershell
   Move-Item textile_waste.db textile_waste_corrupt.db
   ```
3. Copy the verified backup into place:
   ```powershell
   Copy-Item backups\textile_waste_backup_YYYYMMDD_HHMMSS.db textile_waste.db
   ```
4. Restart the backend service.

---

## 6. Health & Liveness Monitoring

The platform provides standardized endpoints compatible with Kubernetes, AWS ECS, Docker Compose, and external monitoring daemons:

### 6.1 Readiness Probe (`GET /health/ready`)
Verifies that all subsystem dependencies are initialized and accepting traffic.

```bash
curl http://127.0.0.1:8000/health/ready
```
Response (HTTP 200 OK):
```json
{
  "status": "ready",
  "checks": {
    "database": "ready",
    "storage": "writable",
    "ai_models": "loaded"
  }
}
```
*Failure behavior:* Returns HTTP 503 Service Unavailable if the database is unreachable, upload directory is read-only, or model files are missing.

### 6.2 Liveness Probe (`GET /health/live`)
Validates that the process event loop is responsive and not deadlocked.

```bash
curl http://127.0.0.1:8000/health/live
```
Response (HTTP 200 OK):
```json
{
  "status": "alive",
  "timestamp": 1794736249.897718
}
```
