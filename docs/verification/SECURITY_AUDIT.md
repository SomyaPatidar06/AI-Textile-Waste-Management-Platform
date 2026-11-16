# Security Audit Report

**Project:** AI Textile Waste Management Platform  
**Target:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Audit Date:** 2026-11-15  
**Auditor:** Independent Security & Verification Engine  
**Overall Risk Assessment:** **LOW RISK / ENTERPRISE READY FOR STAGING**

---

## 1. Threat Model & Scope

The application security audit evaluated the following potential attack vectors across the API, storage, database, and authentication surfaces:

1. **Authentication Bypass & Token Manipulation** (JWT signature forgery, token replay, refresh-token abuse).
2. **Privilege Escalation & RBAC Flaws** (Self-promotion to Admin, unauthorized batch deletion, unauthorized role modification).
3. **Insecure Direct Object Reference (IDOR)** (Viewing/modifying other users' profiles or notifications).
4. **File Upload Vulnerabilities** (Path traversal, shell/executable payload upload, decompression bombs, oversized DoS).
5. **Injection Attacks** (SQL injection, command injection, ORM parameter bypass).
6. **Information Disclosure & Secret Leakage** (Exposed credentials, unmasked secrets, environment variable leakage).
7. **CORS & Cross-Origin Risks** (Overly permissive wildcard origins, unauthorized origin access).

---

## 2. Detailed Security Findings

### 2.1 Authentication & Token Management

- **Password Hashing:** Uses `bcrypt` with automatic random salt generation via `bcrypt.gensalt()`. Plaintext passwords are never stored in memory or persisted to disk. Passwords must be at least 8 characters.
- **JWT Signature & Verification:** Tokens are signed using HMAC-SHA256 (`HS256`).
- **Token Expiration:**
  - Access Tokens: 60 minutes.
  - Refresh Tokens: 7 days.
- **Type Separation:** Tokens contain a `"type"` claim (`"access"` vs `"refresh"`). Dependency validation in `backend/app/api/deps.py` explicitly rejects tokens where `type != "access"`, preventing refresh tokens from being reused to access protected endpoints.
- **Revocation / Invalidation:** Expired tokens and malformed signatures immediately raise HTTP 401 Unauthorized (`ExpiredSignatureError`, `PyJWTError`).

### 2.2 Authorization & Role-Based Access Control (RBAC)

- **Admin Self-Registration Block:** Endpoint `/api/v1/auth/register` explicitly checks the requested role. If `role == RoleEnum.ADMIN`, it raises `HTTP 403 Forbidden` (`"Administrator self-registration is strictly forbidden."`). Initial admins must be created via administrative CLI bootstrap script (`create_initial_admin.py`).
- **Privilege Escalation Prevention:** Non-admin users attempting to update user roles or deactivate accounts via `PUT /api/v1/users/{id}` are rejected with `HTTP 403 Forbidden`.
- **Insecure Direct Object Reference (IDOR) Protection:**
  - User profile updates and queries (`/users/{id}`) enforce that non-admins can only view/edit their own record (`current_user.id == user_id`).
  - Notification management (`/notifications/{id}/read`, `DELETE /notifications/{id}`) checks that the notification belongs to `current_user.id`. Access to another user's notification is rejected with HTTP 403.
- **Sensitive Operations:** Batch deletion (`DELETE /api/v1/batches/{id}`) is strictly restricted to `RoleEnum.ADMIN`.

### 2.3 Upload Security & File Handling

- **Dual-Layer Format Validation:**
  - Layer 1: MIME check against allowed image formats (`image/jpeg`, `image/png`, `image/webp`).
  - Layer 2: Deep binary inspection using `PIL.Image.open(io.BytesIO(file_bytes)).verify()`. This guarantees that files disguised with image extensions (such as `.exe`, `.sh`, `.php`) fail verification and are rejected with HTTP 400.
- **Payload Size Enforcement:** Hard limit of `10 MB` (`10 * 1024 * 1024` bytes). Oversized files are rejected before disk storage.
- **Path Traversal Mitigation:** Untrusted client filenames are never used for disk destination paths. The storage engine constructs file paths using `f"{uuid.uuid4().hex}_{sha256_hash[:12]}{ext}"`. Path characters such as `../`, `..\`, or null bytes are completely rendered inert.
- **SHA-256 Deduplication:** The engine hashes file contents to detect duplicates and verify file integrity.

### 2.4 Database & SQL Injection

- **Query Compilation:** All database operations in repositories and routers use the SQLAlchemy 2.0 ORM query API (`db.query(Model).filter(...)`). Parameters are bound using parameterized SQL placeholders by the SQLAlchemy dialect compiler.
- **Raw SQL Audit:** A static audit across all `.py` files confirmed zero string interpolation or raw SQL concatenation. The only `text()` statement is a static health-check query `conn.execute(text("SELECT 1"))` in `backend/app/main.py`.

### 2.5 Secrets & Environment Configuration

- **Git Tracking Exclusions:** `.gitignore` explicitly excludes `.env`, `.env.local`, `.env.*.local`, `*.pem`, `*.key`, and database files `*.db`, `*.sqlite`.
- **Live Secret Check:** A recursive scan of the repository confirmed zero committed `.env` files or hardcoded private keys.
- **Pydantic Settings:** `backend/app/core/config.py` loads from environment variables with fallback defaults.

### 2.6 CORS & Network Exposure

- **Restricted Origins:** `BACKEND_CORS_ORIGINS` is configured to allow only local development hosts:
  - `http://localhost:3000`
  - `http://localhost:5173`
  - `http://127.0.0.1:3000`
  - `http://127.0.0.1:5173`
- **No Wildcards:** Wildcard origin `"*"` is not used with `allow_credentials=True`.

---

## 3. Vulnerability Findings & Severity Matrix

| ID | Category | Finding Description | Severity | Remediation Status |
|---|---|---|---|---|
| **SEC-01** | Configuration | Fallback `SECRET_KEY` is defined for local dev convenience. In production, this key must be overridden. | **Medium** | Documented condition; recommend adding startup assertion in production mode. |
| **SEC-02** | Database | PostgreSQL enum cleanup on migration downgrade requires explicit drop command. | **Low** | Documented condition; migration works cleanly on SQLite and forward PostgreSQL. |
| **SEC-03** | Rate Limiting | Authentication endpoints currently lack IP-based rate limiting (e.g. slowloris / brute force). | **Low** | Non-blocking for development; recommend adding Redis/slowapi rate limiting before public exposure. |
| **SEC-04** | Deprecation | Starlette status code deprecation warnings in test suite (`HTTP_422_UNPROCESSABLE_ENTITY`). | **Info** | Non-breaking; backward-compatible alias remains supported. |

---

## 4. Remediation Recommendations

1. **Production Secret Key Enforcement:**
   Add a startup check in `backend/app/main.py`:
   ```python
   if settings.ENVIRONMENT == "production" and "dev-secret-key" in settings.SECRET_KEY:
       raise RuntimeError("FATAL: Production environment detected with default SECRET_KEY. Set SECRET_KEY in environment variables.")
   ```

2. **Rate Limiting:**
   Integrate `slowapi` on `/api/v1/auth/login` to limit login attempts to 5 requests per minute per IP address.

3. **Security Headers:**
   Add security response headers middleware (`X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Strict-Transport-Security`).
