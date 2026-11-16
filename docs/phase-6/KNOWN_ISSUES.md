# Phase 6 Known Issues, Operational Observations & Maintenance Notes

**Project:** AI Textile Waste Management Platform  
**Target Specification:** `AI_Textile Waste Intelligence Platform.pdf`  
**Validation Status:** **NO CRITICAL OR BLOCKING ISSUES DETECTED**

---

## 1. Overview

During the Phase 6 end-to-end validation, zero architectural, functional, security, or data integrity blockers were identified. The platform successfully meets all requirements laid out in the authority specification.

This document compiles operational observations, non-blocking environmental characteristics, and recommended maintenance procedures for production facility administrators.

---

## 2. Operational Observations & Characteristics

### A. Optical RGB Visual Estimation Boundary (Option B Policy)
- **Observation:** Standard visible-spectrum RGB optical cameras capture fabric surface weave, texture, and visual pattern. While highly accurate for distinctive weaves (denim, knitted cotton, canvas, silk), RGB optics cannot distinguish microscopic polymer blends (e.g., 65% polyester / 35% cotton vs 50% / 50%) with the molecular precision of wet-chemical dissolution or Near-Infrared (NIR) spectroscopy.
- **Platform Mitigation:** Enforced across all APIs and UI views: every material prediction is prominently labeled `(Visual Estimate)`. When confidence is low or blend ambiguity is detected, the system automatically flags `requires_manual_inspection = True` and sets the uncertainty reason.
- **Production Recommendation:** For high-value recycling streams requiring strict fiber purity guarantees ($> 98\%$), combine the optical camera station with an inline NIR spectrometer sensor.

### B. SQLite vs PostgreSQL Concurrency in High-Throughput Scenarios
- **Observation:** The development environment uses SQLite 3 with WAL mode and `check_same_thread=False`. While ideal for zero-setup local execution, tests, and small single-facility pilots, SQLite utilizes database-level write locking.
- **Platform Mitigation:** The repository already provides a dual-pool connection architecture and a complete multi-container `docker-compose.yml` deploying PostgreSQL with connection pooling (`QueuePool`).
- **Production Recommendation:** Deploy with PostgreSQL when scaling beyond 5 concurrent scanning cameras writing simultaneously.

### C. In-Memory Token Blocklist in Distributed Clusters
- **Observation:** Revoked JWT tokens (logged-out sessions) are currently tracked in memory via `backend/app/core/token_blocklist.py`.
- **Platform Mitigation:** Provides sub-millisecond revocation lookup for single-node FastAPI processes.
- **Production Recommendation:** If scaling horizontally across multiple Uvicorn worker pods behind a load balancer, configure a shared Redis instance for distributed token blocklist state.

---

## 3. Recommended Maintenance Schedule

| Maintenance Task | Recommended Cadence | Operational Command / Script |
| :--- | :---: | :--- |
| **Database Integrity Backup** | Daily | `python backend/scripts/backup_database.py` |
| **Pytest Full Regression** | Pre-Deployment | `pytest backend/tests/ -v` |
| **ONNX Model Graph Validation** | Monthly | `python backend/scripts/phase4_onnx_benchmark.py` |
| **Storage Directory Cleanup** | Quarterly | Archive processed raw image files older than 90 days from `backend/uploads/` |
| **Alembic Schema Sync Check** | On Release | `alembic check` / `alembic upgrade head` |
