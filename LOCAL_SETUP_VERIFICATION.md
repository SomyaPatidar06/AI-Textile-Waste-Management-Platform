# Local Setup & Execution Verification Audit

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Audit Date:** 2026-11-15  
**Auditor:** Engineering Lead / Verification Engine  
**Execution Environment:** Windows 11, Python 3.14.0, Node.js v24.12.0, npm 11.6.2  

---

## 1. Environment & Entry Point Audit

| Component | Target Location | Verification Method | Status |
|---|---|---|---|
| **Backend Main Application** | `backend/app/main.py` | FastAPI lifespan context, router mounting, CORS | **VERIFIED** |
| **Backend Config & Env** | `backend/app/core/config.py` | Pydantic Settings, `.env.example` provided | **VERIFIED** |
| **Database Migrations** | `backend/alembic/` | Alembic SQLite/PostgreSQL configuration | **VERIFIED** |
| **Admin Bootstrap Script** | `backend/scripts/create_initial_admin.py` | Idempotent admin creation script | **VERIFIED** |
| **Frontend Entry Point** | `frontend/src/main.jsx` | React 18 DOM root, Tailwind CSS injection | **VERIFIED** |
| **Frontend Router & Auth** | `frontend/src/App.jsx` | React Router v6, `ProtectedRoute` wrapper | **VERIFIED** |
| **Vite Proxy Integration** | `frontend/vite.config.js` | `/api` ➔ `http://127.0.0.1:8000` proxy | **VERIFIED** |
| **Backend Launch Script** | `start-backend.ps1` | Automatic migration + seed + uvicorn | **VERIFIED** |
| **Frontend Launch Script** | `start-frontend.ps1` | Automatic npm install check + vite dev | **VERIFIED** |

---

## 2. Verbatim Test Evidence

### 2.1 Manual QA End-to-End Workflow Audit Script

Executed `python backend/scripts/manual_qa_verification.py` against live application:

```
======================================================================
AI Textile Waste Management Platform - Manual QA Workflow Audit
======================================================================
[QA-01] Health check: PASSED (db: connected, environment: development)
[QA-02] Admin authentication: PASSED (JWT access & refresh tokens issued)
[QA-03] JWT token refresh: PASSED
[QA-04] Admin self-registration rejection: PASSED (HTTP 403 Forbidden)
[QA-05] Operator registration: PASSED
[QA-06] Recycler registration: PASSED
[QA-07] Operator profile ingestion: PASSED (role=OPERATOR)
[QA-08] RBAC user management access controls: PASSED (Operator 403, Admin 200)
[QA-09] Batch creation: PASSED (id=bd460d11-d325-4412-a8c2-ace4ba58342a, code=BATCH-QA-VERIF-001, weight=175.5 kg)
[QA-10] Batch status transitions (COLLECTED -> SORTED -> PROCESSED): PASSED
[QA-11] Immutable audit trail verification: PASSED (3 status log entries)
[QA-12] Upload security guards (Empty 400, Oversized 413, Corrupt 400): PASSED
[QA-13] Multi-task AI scan: PASSED (Material='Polyester (Visual Estimate)', Defect='Defect Free', Score=57.0/100)
[QA-14] In-app notifications & IDOR ownership controls: PASSED
[QA-15] ESG summary metrics: PASSED (Diverted=175.5 kg, CO2 Avoided=1491.75 kg)
[QA-16] CSV stream export: PASSED (1 rows exported)
[QA-17] Digital circularity certificate: PASSED (Certificate ID: CERT-BATCH-QA-VERIF-001, Status: DOWN_CYCLING_REQUIRED)
[QA-18] Operator batch deletion rejection: PASSED (HTTP 403 Forbidden)
======================================================================
ALL 18 MANUAL QA WORKFLOW AUDITS PASSED WITH ZERO FAILURES!
======================================================================
```

---

### 2.2 Backend Regression Test Suite

Executed `python -m pytest backend/tests -v --tb=short`:

```
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.0.2, pluggy-1.6.0 -- C:\Program Files\Python314\python.exe
cachedir: .pytest_cache
rootdir: D:\Textile-Waste-Workspace
plugins: anyio-4.12.0, asyncio-1.3.0
asyncio: mode=Mode.STRICT, debug=False, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
collecting ... collected 41 items

AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_material_engine_option_b_governance PASSED [  2%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_defect_engine_provisional_threshold_and_uncertainty PASSED [  4%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_defect_engine_low_threshold_override PASSED [  7%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_dataset_provenance_manager PASSED [  9%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_dedicated_material_trainer_evaluation PASSED [ 12%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_material_trainer_stratified_split_and_leakage PASSED [ 14%]
AI-Textile-Waste-Management-Platform/backend/tests/test_ai_modules.py::test_material_trainer_learning_curves_and_checkpoint PASSED [ 17%]
AI-Textile-Waste-Management-Platform/backend/tests/test_analysis_api.py::test_scan_textile_image PASSED [ 19%]
AI-Textile-Waste-Management-Platform/backend/tests/test_analysis_api.py::test_list_and_filter_analyses PASSED [ 21%]
AI-Textile-Waste-Management-Platform/backend/tests/test_analysis_api.py::test_get_metrics_summary PASSED [ 24%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_health_check PASSED [ 26%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_login_success PASSED [ 29%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_login_invalid_password PASSED [ 31%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_login_unknown_user PASSED [ 34%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_public_register_success PASSED [ 36%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_public_register_admin_forbidden PASSED [ 39%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_register_duplicate_user PASSED [ 41%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_refresh_token PASSED [ 43%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_me_authenticated PASSED [ 46%]
AI-Textile-Waste-Management-Platform/backend/tests/test_auth.py::test_me_unauthenticated PASSED [ 48%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_create_batch_success PASSED [ 51%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_create_duplicate_batch_rejected PASSED [ 53%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_create_batch_negative_weight_rejected PASSED [ 56%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_list_and_filter_batches PASSED [ 58%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_batch_status_lifecycle_and_history PASSED [ 60%]
AI-Textile-Waste-Management-Platform/backend/tests/test_inventory.py::test_delete_batch_admin_only PASSED [ 63%]
AI-Textile-Waste-Management-Platform/backend/tests/test_notifications.py::test_in_app_notifications_lifecycle PASSED [ 65%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_list_users_as_admin_allowed PASSED [ 68%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_list_users_as_operator_forbidden PASSED [ 70%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_list_users_as_recycler_forbidden PASSED [ 73%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_cross_user_profile_access_blocked PASSED [ 75%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_admin_can_update_user_role PASSED [ 78%]
AI-Textile-Waste-Management-Platform/backend/tests/test_rbac.py::test_operator_cannot_escalate_own_role PASSED [ 80%]
AI-Textile-Waste-Management-Platform/backend/tests/test_reports_api.py::test_esg_summary_report PASSED [ 82%]
AI-Textile-Waste-Management-Platform/backend/tests/test_reports_api.py::test_export_analyses_csv PASSED [ 85%]
AI-Textile-Waste-Management-Platform/backend/tests/test_reports_api.py::test_batch_recycling_certificate PASSED [ 87%]
AI-Textile-Waste-Management-Platform/backend/tests/test_storage.py::test_valid_jpeg_upload PASSED [ 90%]
AI-Textile-Waste-Management-Platform/backend/tests/test_storage.py::test_valid_png_upload PASSED [ 92%]
AI-Textile-Waste-Management-Platform/backend/tests/test_storage.py::test_corrupt_image_rejected PASSED [ 95%]
AI-Textile-Waste-Management-Platform/backend/tests/test_storage.py::test_empty_file_rejected PASSED [ 97%]
AI-Textile-Waste-Management-Platform/backend/tests/test_storage.py::test_oversized_file_rejected PASSED [100%]

======================= 41 passed, 2 warnings in 54.48s =======================
```

---

### 2.3 Frontend Production Build

Executed `npm run build --prefix frontend`:

```
> ai-textile-waste-platform-frontend@2.0.0 build
> vite build

vite v5.4.21 building for production...
transforming...
✓ 1571 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.53 kB │ gzip:  0.35 kB
dist/assets/index-Ct9k2NHy.css   23.24 kB │ gzip:  4.92 kB
dist/assets/index-MV6NLHzn.js   291.02 kB │ gzip: 89.24 kB
✓ built in 11.08s
```

---

## 3. Confirmed Bugs Identified & Resolved

During hands-on inspection, two functional integration issues were discovered and immediately resolved:

### BUG-01: CSV Export Authentication Failure in Browser
- **Symptom:** Clicking **Export Analyses CSV** opened a new browser tab via `window.open('/api/v1/reports/export/csv', '_blank')`. Because the browser's native GET does not carry the SPA's Bearer JWT from `localStorage`, the backend rejected the request with `HTTP 401 Unauthorized` (`"Not authenticated"`).
- **Resolution:** Replaced `window.open` with an authenticated Axios request (`api.get('/reports/export/csv', { responseType: 'blob' })`) that programmatically generates an ephemeral download link using `URL.createObjectURL(blob)`. The CSV now downloads securely with full JWT authorization.
- **Affected File:** `frontend/src/pages/Reports.jsx`.

### BUG-02: Empty String Foreign Key Handling in Scan Endpoint
- **Symptom:** When a user uploaded an image without selecting an inventory batch, the form submitted `batch_id=""` (empty string). In databases with strict foreign key constraints, assigning `""` rather than `None` to a foreign key column causes an integrity violation because no batch with an empty string ID exists.
- **Resolution:** Sanitized `batch_id` in `backend/app/api/v1/analysis.py` to `batch_id.strip() or None` and assigned `batch.id if batch else None` to `AnalysisRecord`.
- **Affected File:** `backend/app/api/v1/analysis.py`.

---

## 4. AI Evaluation Infrastructure Readiness (Phase 3 Preparation)

In accordance with Section 5 requirements, the training and evaluation infrastructure in `backend/app/ai/training/` was expanded and verified:

1. **Duplicate Detection:** `DatasetProvenanceManager.detect_duplicates()` scans directories, computes SHA-256 hashes, and flags duplicate image pairs.
2. **Stratified Splitting with Zero Leakage:** `DedicatedMaterialTrainer.partition_dataset_stratified()` partitions samples across classes with a 70/15/15 ratio, strictly checking that identical image hashes do not cross partition boundaries.
3. **Loss Curve Tracking:** `record_epoch()` tracks training loss, validation loss, and validation accuracy per epoch.
4. **Checkpoint Versioning:** `save_checkpoint_metadata()` outputs structured JSON records containing hyperparameters, evaluation metrics, and convergence histories.
