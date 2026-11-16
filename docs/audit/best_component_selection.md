# Best-of-Breed Component Selection Matrix

**Principle:** Select the empirically superior component from all 16 reference repositories. Do not force loyalty to any single codebase. Combine the strongest verified modules into a unified, secure, and production-grade architecture.

---

## 1. Master Component Selection Matrix

| Subsystem / Component | Best Source Repository | Exact Source File Reference | Empirical Verification & Evidence | Recommended Action for Target Project |
|---|---|---|---|---|
| **1. Frontend Architecture & UI Layout** | **R15** (Srilakshmi) | `frontend/src/App.jsx`, `components/RoleDashboards.jsx`, `components/ui.jsx` | Mature React 18 SPA with dark sustainability aesthetic, 4 role-based dashboards (Admin, Operator, ESG, Manufacturer), and responsive Tailwind components. | **ADAPT:** Use as the UI foundation. Patch upload batch ID tracking and integrate multi-model inference badges. |
| **2. Backend Routing & Structure** | **R4** (SorTexAI) + **R1** (Repo 6) | R4 `backend/main.py`, `ml_endpoints.py`, `sustainability_endpoints.py`; R1 `backend/app/main.py` | Modern FastAPI lifespan architecture with clean modular routers (`APIRouter`), background task scheduling, and clean dependency injection. | **ADAPT:** Combine SorTexAI's modular router decomposition with Repo 6's clean Pydantic v2 validation schemas. |
| **3. Authentication & RBAC** | **R1** (Repo 6) + **R15** (Srilakshmi) | R1 `backend/app/schemas.py` lines 14-45; R15 `backend/app/auth.py` | R1 defines typed `RoleEnum` with strict validation that prevents public admin registration; R15 provides JWT token creation and bcrypt hashing. | **REWRITE:** Combine Bcrypt password hashing with R1's role whitelisting and a fixed database revocation check (`revoked = FALSE`). |
| **4. Database Models & Schema** | **R1** (Repo 6) | `backend/app/models.py` (lines 1-72) | The only true SQLAlchemy 2.0 declarative ORM implementation: UUID primary keys, typed enums, and a dedicated `StatusHistory` table tracking the full audit trail. | **ADAPT:** Adopt R1's declarative models as the core schema, adding PostgreSQL native `JSONB` for raw CV feature archiving. |
| **5. Material Classification (Natural Fibres)** | **R9** (Abinash Mohapatra) | `backend/fabric_model_v2.pth`, `train_model.py` | PyTorch ResNet-18 model with verified **95.45% validation accuracy** and **92.75% test accuracy** across 6 natural fibres (`Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool`). | **RETAIN & INTEGRATE:** Import weights into `app/ml_models/` and wrap in an async PyTorch inference service. |
| **6. Material Classification (Commercial Blends)** | **R4** (SorTexAI) | `ml_engine/models/material_classifier.pt`, `taxonomy.json` | 11-class PyTorch ResNet-18 covering commercial blends (`Poly-Cotton Blend`, `Denim`, `Polyester`, `Viscose`, `Nylon`). | **RETAIN & INTEGRATE:** Deploy alongside R9 model as secondary classifier for blended synthetic/commercial waste. |
| **7. Fabric Defect Detection** | **R13** (Thanmayee) + **R14** (Repo 7) | R13 `model/fabric_defect_model.keras`; R14 `backend/ml_service.py` (lines 46-52, 121-175) | R13 provides a 9-class MobileNetV2 defect CNN (77% accuracy); R14 provides a hybrid 70% confidence gate that falls back to OpenCV contour detection for structural tears/holes. | **ADAPT:** Integrate R13's 9-class defect model governed by R14's hybrid confidence-gating architecture. |
| **8. Image Preprocessing Pipeline** | **R9** (Abinash) + **R4** (SorTexAI) | R9 `train_model.py` (lines 62-72); R4 `ml_engine/serve.py` (lines 20-24) | Standardized Torchvision transforms with ImageNet mean `[0.485, 0.456, 0.406]` and std `[0.229, 0.224, 0.225]`, matching ResNet-18 weights. | **RETAIN:** Standardize all deep learning inputs on $224 \times 224$ RGB ImageNet normalized tensors. |
| **9. Quality Assessment & Texture Analysis** | **R15** (Srilakshmi) + **R4** (SorTexAI) | R15 `backend/app/cv_analysis.py` (lines 73-124); R4 `ml_engine/texture_pattern_analyzer.py` | GLCM texture properties (contrast, homogeneity, energy, smoothness) combined with 2D FFT spectral regularity to output texture quality ratings (`GOOD`, `AVERAGE`, `POOR`). | **ADAPT:** Combine Srilakshmi's GLCM metrics with SorTexAI's pattern classifier (`Solid`, `Striped`, `Plaid/Check`, `Patterned`). |
| **10. Recycling Recommendation Engine** | **R4** (SorTexAI) + **R15** (Srilakshmi) | R4 `ml_engine/recyclability_engine.py`; R15 `backend/app/scoring.py` (lines 102-176) | SorTexAI provides granular industrial matrices for mechanical and chemical recycling; Srilakshmi provides actionable multi-tiered disposal rules. | **ADAPT:** Fuse SorTexAI's recyclability scores with Srilakshmi's 7-tier recommendation engine. |
| **11. Sustainability & ESG Benchmarking** | **R15** (Srilakshmi) | `backend/app/scoring.py` (lines 178-234), `main.py` (lines 806-865) | Formulaic carbon ($4.2 \text{ kg CO}_2 / 100\text{ score}$) and water ($2650 \text{ L} / 100\text{ score}$) savings, with industry average (52.0) vs. best-in-class (82.0) benchmarking. | **ADAPT:** Retain Srilakshmi's circularity scoring formula and ESG benchmark comparative analytics. |
| **12. Reporting & Document Export** | **R15** (Srilakshmi) | `backend/app/main.py` (lines 631-687, 713-865) | Complete ReportLab PDF generation (single-item, batch, and sustainability certificates) and OpenPyXL Excel streaming. | **ADAPT:** Extract ReportLab canvas routines into a dedicated `services/pdf_generator.py` service. |
| **13. Inventory Management** | **R1** (Repo 6) + **R15** (Srilakshmi) | R1 `backend/app/models.py` (Batch & StatusHistory); R15 `frontend/src/pages/Inventory.jsx` | R1 provides the backend batch tracking schema with audit logs; R15 provides the interactive web CRUD table. | **ADAPT:** Pair R15's frontend table with R1's relational `batches` and `status_history` backend API. |
| **14. Notifications & Alerts** | **R15** (Srilakshmi) + **R4** (SorTexAI) | R15 `backend/app/notifications.py`, `NotificationBell.jsx`; R4 `notifications_scheduler.py` | R15 generates event-driven alerts for recycling opportunities and hazardous materials; R4 provides background scheduled jobs. | **ADAPT:** Retain R15's notification bell and preference controls, driven by FastAPI background tasks. |
| **15. Containerization & Deployment** | **R15** (Srilakshmi) | `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` | Multi-container setup with backend, frontend, PostgreSQL, and volume mounts. | **ADAPT:** Update compose configuration to orchestrate PostgreSQL 16, FastAPI (Python 3.11-slim), and React (Nginx alpine). |

---

## 2. Key Paradigm Shift from Initial Phase 1 Audit

In the initial Phase 1 audit, our options appeared limited to:
* Primary (Srilakshmi): No trained models; rule-based heuristics only.
* Secondary (Thanmayee): A defect model mislabeled as a material classifier.

**The Multi-Repository Discovery has fundamentally transformed our technical strategy:**
1. We now possess **two authentic, trained fabric material classifiers**:
   - Abinash Mohapatra's **ResNet-18 model (92.75% test accuracy)** for natural fibres (`Cotton`, `Wool`, `Silk`, `Linen`, `Hessian`, `Abaca`).
   - SorTexAI's **ResNet-18 model** for commercial blends and synthetics (`Polyester`, `Poly-Cotton Blend`, `Nylon`, `Viscose`, `Denim`).
2. We possess a **production-ready SQLAlchemy 2.0 ORM architecture** (from Repo 6) with UUID keys, `StatusHistory` audit trails, and strict role validation.
3. We have an **industrial recyclability knowledge base** (from SorTexAI) to replace simplistic hardcoded lookups.

By selectively uniting these verified components, our target platform becomes vastly superior to any individual reference repository.
