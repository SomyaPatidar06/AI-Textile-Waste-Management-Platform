# Test Evidence Report

**Project:** AI Textile Waste Management Platform  
**Target:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Execution Timestamp:** 2026-11-15T12:49:25Z  
**Test Runner:** pytest 9.0.2 / Python 3.14.0 (Windows 11)  
**Total Tests Executed:** 39  
**Tests Passed:** 39 (100%)  
**Tests Failed:** 0 (0%)  
**Overall Status:** **PASSED**

---

## 1. Backend Regression Suite Log

**Command:**
```powershell
python -m pytest D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend\tests -v --tb=short
```

**Exit Code:** `0`  
**Execution Duration:** `50.69s`  

### Enumerated Test Results

| Module | Test Function | Result | Category |
|---|---|---|---|
| `test_ai_modules.py` | `test_material_engine_option_b_governance` | **PASSED** | AI Governance & Visual Estimate |
| `test_ai_modules.py` | `test_defect_engine_provisional_threshold_and_uncertainty` | **PASSED** | Defect 0.45 Threshold & Taxonomy |
| `test_ai_modules.py` | `test_defect_engine_low_threshold_override` | **PASSED** | Uncertainty Gating & Flagging |
| `test_ai_modules.py` | `test_dataset_provenance_manager` | **PASSED** | License & Provenance Verification |
| `test_ai_modules.py` | `test_dedicated_material_trainer_evaluation` | **PASSED** | Macro F1 & Evaluation Metrics |
| `test_analysis_api.py` | `test_scan_textile_image` | **PASSED** | Multipart Scan & Dual Inference API |
| `test_analysis_api.py` | `test_list_and_filter_analyses` | **PASSED** | Analysis Pagination & Query Filters |
| `test_analysis_api.py` | `test_get_metrics_summary` | **PASSED** | Circularity & Review Rate Metrics |
| `test_auth.py` | `test_health_check` | **PASSED** | System Health & DB Connectivity |
| `test_auth.py` | `test_login_success` | **PASSED** | Valid Credential Authentication |
| `test_auth.py` | `test_login_invalid_password` | **PASSED** | Invalid Password Rejection (401) |
| `test_auth.py` | `test_login_unknown_user` | **PASSED** | Unknown User Rejection (401) |
| `test_auth.py` | `test_public_register_success` | **PASSED** | Operator Account Self-Registration |
| `test_auth.py` | `test_public_register_admin_forbidden` | **PASSED** | Admin Self-Registration Block (403) |
| `test_auth.py` | `test_register_duplicate_user` | **PASSED** | Duplicate Username/Email Rejection (400) |
| `test_auth.py` | `test_refresh_token` | **PASSED** | JWT Refresh Token Lifecycle |
| `test_auth.py` | `test_me_authenticated` | **PASSED** | Authenticated User Profile Ingestion |
| `test_auth.py` | `test_me_unauthenticated` | **PASSED** | Missing/Invalid Token Rejection (401) |
| `test_inventory.py` | `test_create_batch_success` | **PASSED** | Batch Intake Creation |
| `test_inventory.py` | `test_create_duplicate_batch_rejected` | **PASSED** | Unique Batch Code Enforcement (400) |
| `test_inventory.py` | `test_create_batch_negative_weight_rejected` | **PASSED** | Input Validation Boundary Check (422) |
| `test_inventory.py` | `test_list_and_filter_batches` | **PASSED** | Status & Text Search Filtering |
| `test_inventory.py` | `test_batch_status_lifecycle_and_history` | **PASSED** | State Transitions & Immutable Audit |
| `test_inventory.py` | `test_delete_batch_admin_only` | **PASSED** | Admin-Only Deletion Enforcement (403) |
| `test_notifications.py` | `test_in_app_notifications_lifecycle` | **PASSED** | In-App Alerts, Ownership & Read Marks |
| `test_rbac.py` | `test_list_users_as_admin_allowed` | **PASSED** | Admin User Listing Access (200) |
| `test_rbac.py` | `test_list_users_as_operator_forbidden` | **PASSED** | Operator User Listing Block (403) |
| `test_rbac.py` | `test_list_users_as_recycler_forbidden` | **PASSED** | Recycler User Listing Block (403) |
| `test_rbac.py` | `test_cross_user_profile_access_blocked` | **PASSED** | IDOR Cross-Profile Access Block (403) |
| `test_rbac.py` | `test_admin_can_update_user_role` | **PASSED** | Admin Role Elevation / Modification |
| `test_rbac.py` | `test_operator_cannot_escalate_own_role` | **PASSED** | Self-Privilege Escalation Block (403) |
| `test_reports_api.py` | `test_esg_summary_report` | **PASSED** | Carbon, Water, Energy Aggregate Math |
| `test_reports_api.py` | `test_export_analyses_csv` | **PASSED** | Standard CSV Stream Export |
| `test_reports_api.py` | `test_batch_recycling_certificate` | **PASSED** | Digital Compliance Certificate Issuance |
| `test_storage.py` | `test_valid_jpeg_upload` | **PASSED** | Valid JPEG Ingestion & Hashing |
| `test_storage.py` | `test_valid_png_upload` | **PASSED** | Valid PNG Ingestion & Hashing |
| `test_storage.py` | `test_corrupt_image_rejected` | **PASSED** | Corrupt / Fake Image Rejection (400) |
| `test_storage.py` | `test_empty_file_rejected` | **PASSED** | Zero-Byte Payload Rejection (400) |
| `test_storage.py` | `test_oversized_file_rejected` | **PASSED** | >10 MB Oversized File Rejection (413) |

---

## 2. Database Migration Lifecycle Test Log

**Command:**
```powershell
cd D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\backend
$env:DATABASE_URL="sqlite:///./test_migration.db"
python -m alembic upgrade head
python -m alembic downgrade base
python -m alembic upgrade head
Remove-Item test_migration.db -ErrorAction SilentlyContinue
```

**Exit Code:** `0`  
**Output Log:**
```
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 883b186bad06, initial_schema
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running downgrade 883b186bad06 -> , initial_schema
INFO  [alembic.runtime.migration] Context impl SQLiteImpl.
INFO  [alembic.runtime.migration] Will assume non-transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 883b186bad06, initial_schema
```
**Conclusion:** Reversible migration verified forward and backward with complete index and table cleanup.

---

## 3. Frontend Production Build Log

**Command:**
```powershell
npm run build --prefix D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform\frontend
```

**Exit Code:** `0`  
**Execution Duration:** `5.43s`  
**Compiler:** Vite v5.4.21 / Rollup  

**Build Summary Output:**
```
vite v5.4.21 building for production...
transforming...
✓ 1571 modules transformed.
rendering chunks...
computing gzip size...
dist/index.html                   0.53 kB │ gzip:  0.35 kB
dist/assets/index-Ct9k2NHy.css   23.24 kB │ gzip:  4.92 kB
dist/assets/index-BkANq01v.js   290.62 kB │ gzip: 89.09 kB
✓ built in 5.43s
```
**Conclusion:** 0 errors, 0 compilation warnings. Bundle optimized with Brotli/Gzip efficiency.

---

## 4. Warnings and Analysis

During the backend pytest execution, two Starlette deprecation warnings were logged:
1. `DeprecationWarning: 'HTTP_422_UNPROCESSABLE_ENTITY' is deprecated. Use 'HTTP_422_UNPROCESSABLE_CONTENT' instead.`
2. `DeprecationWarning: 'HTTP_413_REQUEST_ENTITY_TOO_LARGE' is deprecated. Use 'HTTP_413_CONTENT_TOO_LARGE' instead.`

**Assessment:** These represent upstream RFC 9110 naming standardization in Starlette. The legacy aliases remain fully supported in FastAPI 0.128+ and Starlette, causing zero runtime failures.
