# Security and License Audit Report

**Target Scope:** `reference-repositories/textile-waste-intelligence-platform-main` & `reference-repositories/Textile-Waste-management-platform-main`  
**Audit Standard:** OWASP Top 10 API Security Risks & Open Source Licensing Compliance  
**Date:** 2026-11-15  
**Policy Compliance:** No real credentials, API tokens, or actual secret keys are printed in plain text.

---

## 1. Vulnerability Findings Matrix

| Vulnerability ID | Category | Severity | Affected Repository | Source Location | Description & Impact | Remediation Requirement |
|---|---|---|---|---|---|---|
| **VULN-01** | Broken Authentication / Privilege Escalation | **CRITICAL** | Primary (FastAPI) | `backend/app/main.py` lines 57-69 | Public registration endpoint `/api/auth/register` accepts arbitrary `role` from payload. Any unauthenticated caller can register with `"role": "admin"`. | Whitelist registration roles to basic tier (`manufacturer`, `recycling_operator`). Admin accounts must require approval or internal seeding. |
| **VULN-02** | Plaintext Password Storage | **CRITICAL** | Secondary (Flask) | `backend/routes/auth.py` lines 25, 49 | Passwords stored and checked in plain text without hashing (`user.password != password`). Compromise of database exposes all user credentials immediately. | Enforce Argon2id or Bcrypt with work factor $\ge 12$. |
| **VULN-03** | Broken Token Revocation | **HIGH** | Primary (FastAPI) | `backend/app/main.py` lines 95-106 | `/api/auth/refresh` checks token type but **never queries the `revoked` column** in `refresh_tokens`. Revoked or logged-out tokens remain valid. | Add active query check: `SELECT revoked FROM refresh_tokens WHERE token = :t AND revoked = FALSE`. |
| **VULN-04** | Hardcoded Secrets & Unsafe Defaults | **HIGH** | Primary (FastAPI) | `backend/app/auth.py` line 12, `database.py` line 21 | Fallback JWT secret key (`textile-waste-dev-secret-...`) and database connection string with default credentials embedded directly in source. | Require mandatory environment variables in production. Halt startup if default secrets are detected. |
| **VULN-05** | Insecure CORS Configuration | **HIGH** | Primary (FastAPI) | `backend/app/main.py` lines 36-42 | `allow_origins=["*"]` configured simultaneously with `allow_credentials=True`. Modern browsers block this configuration, while misconfigured proxies risk token leakage. | Explicitly configure allowed origins whitelist (e.g. `http://localhost:5173`, production domains). |
| **VULN-06** | Dynamic SQL Column Interpolation | **MEDIUM** | Primary (FastAPI) | `backend/app/main.py` lines 133, 429 | Dynamic SQL column generation via `f"{k}=:{k}"` in UPDATE statements. If Pydantic schemas allow additional fields, this allows SQL injection or column tampering. | Whitelist updateable columns explicitly or use SQLAlchemy ORM attributes. |
| **VULN-07** | Missing Authentication on State Endpoints | **CRITICAL** | Secondary (Flask) | `backend/routes/inventory.py`, `backend/routes/predict.py` | All inventory CRUD (`POST`, `PUT`, `DELETE /inventory`) and AI prediction endpoints have zero authentication decorators. Anyone on the internet can mutate inventory. | Enforce JWT token verification on all protected endpoints. |
| **VULN-08** | Incomplete File Upload Validation | **MEDIUM** | Both Repositories | Primary `main.py` line 451, Secondary `predict.py` line 155 | Images are uploaded without MIME-type magic byte validation or file size limits, risking memory exhaustion (DoS) or path traversal (`os.path.join(upload_folder, file.filename)`). | Validate file magic bytes (`python-magic`), sanitize filenames (`werkzeug.utils.secure_filename`), and enforce strict file size caps. |
| **VULN-09** | Email Service Credential Exposure Risk | **MEDIUM** | Secondary (Flask) | `backend/services/email_service.py` lines 17-23 | Plain SMTP authentication without rate-limiting or anti-relay protection. If SMTP credentials are set in environment, arbitrary users can abuse endpoint `/reports/email` to send spam. | Add rate-limiting, strict email recipient validation, and authenticated session constraints. |

---

## 2. In-Depth Security Subsystem Audits

### 2.1 Password Storage & Authentication
* **Primary (FastAPI):**
  - Uses `passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")`.
  - Password hashing is technically robust with Bcrypt salt.
  - However, pre-seeded admin user in `backend/app/database.py` lines 147-148 creates account `admin@textilewaste.ai` with a known static password on clean database initialization.
* **Secondary (Flask):**
  - Completely absent. Model `User` (`backend/models/user.py`) stores string passwords in plain text.
  - Registration in `backend/routes/auth.py` commits plain text passwords directly.
  - Authentication returns user ID without issuing a secure token.

### 2.2 JWT & Session Management
* **Primary (FastAPI):**
  - Generates HS256 tokens using `python-jose`.
  - Access token expiration: 30 minutes.
  - Refresh token expiration: 7 days.
  - Refresh token table exists in database (`refresh_tokens`), and `/api/auth/logout` sets `revoked = 1`.
  - **The Defect:** In `main.py` lines 95-106 (`refresh_token` function):
    ```python
    @app.post("/api/auth/refresh")
    def refresh_token(payload: RefreshRequest):
        data = decode_token(payload.refresh_token)
        if data.get("type") != "refresh":
            raise HTTPException(401, "Invalid refresh token")
        with db_session() as conn:
            row = conn.execute(
                text("SELECT id, role FROM users WHERE id=:id"), {"id": int(data["sub"])}
            ).mappings().first()
        if not row:
            raise HTTPException(401, "User not found")
        return {"access_token": create_access_token(row["id"], row["role"]), "token_type": "bearer"}
    ```
    The token revocation table is **never queried**. A revoked refresh token can be used indefinitely until token expiration.

### 2.3 SQL Injection & ORM Analysis
* Neither repository uses parameterized ORM models properly:
  - Secondary uses Flask-SQLAlchemy with `User.query.filter_by(email=email)`, which is safe from injection, but lacks authentication.
  - Primary uses raw SQLAlchemy `text()` with parameters, which prevents direct value injection (`WHERE email=:e`), BUT dynamically interpolates column names in update routes:
    ```python
    set_clause = ", ".join([f"{k}=:{k}" for k in fields])
    conn.execute(text(f"UPDATE users SET {set_clause} WHERE id=:id"), {**fields, "id": user["id"]})
    ```
    If fields are not strictly sanitised, attacker-controlled keys can corrupt database statements.

---

## 3. Intellectual Property, Licensing, and Attribution Audit

| Category | Primary Repository | Secondary Repository | Target Project Compliance Status |
|---|---|---|---|
| **Software License** | MIT License (Copyright 2026 Srilakshmi Kommu) | MIT License (Copyright 2026 Thanmayee Nadimpalli) | Both repositories are open source under the permissive MIT license. Compatible with commercial and proprietary reuse provided copyright notices and permission notices are retained. |
| **Model Weights License** | N/A (No model weights committed) | Unspecified (Weights committed in git without explicit license header) | Keras weights `best_model.keras` and `textile_model.keras` fine-tune Google's `MobileNetV2` (Apache License 2.0). Permissive, but model license must be declared formally. |
| **Dataset License** | N/A (Ten Fabrics Dataset referenced, not committed) | N/A (Defect dataset referenced, not committed) | Neither repository includes the underlying image datasets. The Ten Fabrics Dataset and Kaggle fabric defect datasets carry academic/research terms. Our target repository must document exact dataset provenance and licensing. |
| **Third-Party Libraries** | FastAPI, React, OpenCV, Tailwind, ReportLab, Pydantic, SQLAlchemy, Pytest | Flask, React, TensorFlow, Keras, Recharts, jsPDF, Lucide | All dependencies use permissive licenses (MIT, BSD-3, Apache 2.0). ReportLab is open-source BSD. |

### Licensing Action Plan:
1. Retain MIT license in our root `LICENSE` file.
2. Maintain a `THIRD_PARTY_NOTICES.md` acknowledging Srilakshmi Kommu and Thanmayee Nadimpalli for reference architectures.
3. Explicitly document that image datasets (when acquired) must be governed by their respective public data licenses (e.g. CC BY-SA or Kaggle Open Data).
