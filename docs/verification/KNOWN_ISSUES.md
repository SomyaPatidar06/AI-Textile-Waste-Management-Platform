# Known Issues & Technical Debt Register

**Project:** AI Textile Waste Management Platform  
**Target:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Review Date:** 2026-11-15  
**Classification:** Non-blocking items, edge cases, and architectural enhancements.

---

## 1. Register of Known Issues

### ISSUE-01: Development Fallback `SECRET_KEY`
- **Location:** `backend/app/core/config.py` (Line 11)
- **Description:** A default fallback secret key (`"dev-secret-key-change-in-production-092837492837"`) is provided for developer convenience in local environments.
- **Risk Level:** Low in development; Critical if deployed to production without an environment variable.
- **Remediation Plan:** Add a startup guard in `backend/app/main.py` that raises a fatal exception if `ENVIRONMENT == "production"` and the default string is detected.

### ISSUE-02: PostgreSQL Enum Teardown during Downgrade
- **Location:** `backend/alembic/versions/883b186bad06_initial_schema.py`
- **Description:** When running `alembic downgrade base` on PostgreSQL, `op.drop_table()` drops the tables, but PostgreSQL retains the custom `ENUM` types (`roleenum`, `batchstatusenum`, `notificationcategoryenum`) in `pg_type`.
- **Risk Level:** Low. Forward migrations and SQLite migrations operate without issue. Re-running `upgrade head` after a downgrade on PostgreSQL can trigger `type already exists`.
- **Remediation Plan:** Add explicit `sa.Enum(name='roleenum').drop(op.get_bind(), checkfirst=True)` statements in the downgrade block for PostgreSQL deployments.

### ISSUE-03: Starlette HTTP Status Code Deprecation Warnings
- **Location:** `backend/app/services/storage.py` and `backend/tests/test_storage.py`
- **Description:** Starlette / FastAPI deprecated `HTTP_422_UNPROCESSABLE_ENTITY` and `HTTP_413_REQUEST_ENTITY_TOO_LARGE` in favor of RFC 9110 naming (`HTTP_422_UNPROCESSABLE_CONTENT` and `HTTP_413_CONTENT_TOO_LARGE`).
- **Risk Level:** Negligible. Aliases remain fully functional with 0 runtime errors.
- **Remediation Plan:** Standardize constants to modern Starlette names during routine code maintenance.

### ISSUE-04: Frontend Table Pagination Controls
- **Location:** `frontend/src/pages/Inventory.jsx` and `frontend/src/pages/Dashboard.jsx`
- **Description:** The backend API supports `skip` and `limit` pagination parameters, but the frontend views currently display the top 50 or 100 records in scrollable tables without pagination controls (Next/Previous/Page numbers).
- **Risk Level:** Low. Sufficient for hundreds of batches; high-volume production datasets will require pagination buttons.
- **Remediation Plan:** Implement pagination controls and page-size selector in the inventory table.

### ISSUE-05: Real-Time Notification Delivery (WebSocket / SSE)
- **Location:** `frontend/src/components/NotificationBell.jsx`
- **Description:** The frontend currently polls `/notifications/unread-count` and `/notifications` every 15 seconds.
- **Risk Level:** Low. Standard polling pattern that works cleanly for small to medium installations without persistent socket overhead.
- **Remediation Plan:** Implement a Server-Sent Events (SSE) or WebSocket route in Phase 3 for sub-second notification dispatch.

### ISSUE-06: Pretrained Deep Learning Checkpoints Pending Training
- **Location:** `backend/app/ai/material_engine.py`
- **Description:** Per user-approved Option B governance, natural/synthetic material classification is currently running under visual estimation rules with manual inspection gating until an independent, licensed dataset is acquired and trained in Phase 3.
- **Risk Level:** Informational. System behaves safely by refusing to invent misleading certified claims.
- **Remediation Plan:** Execute Phase 3 dedicated training pipeline (`train_material.py`) once the dataset manifest is finalized.

### ISSUE-07: Defect Detection Spatial Bounding Boxes
- **Location:** `backend/app/ai/defect_engine.py`
- **Description:** Defect classification operates at the image level (7 classes: Defect Free, Stain, Hole, Broken Stitch, Needle Mark, Pinched Fabric, Weave Defect). Bounding box spatial localization is marked as planned for Phase 3.
- **Risk Level:** Informational. Explicitly communicated in API responses and frontend notices.
- **Remediation Plan:** Integrate YOLOv8 object detection model with bounding box coordinates in Phase 3.
