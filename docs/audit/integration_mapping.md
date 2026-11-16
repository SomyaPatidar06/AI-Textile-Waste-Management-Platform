# File-Level Integration and Migration Matrix

**Target Architecture:**
* **Frontend:** Single React 18+ SPA (Vite + Tailwind CSS + Lucide Icons + Recharts / Chart.js)
* **Backend:** Single Python FastAPI REST API (Async, Pydantic v2, Clean Service Architecture)
* **Database:** Single PostgreSQL 16 Instance with SQLAlchemy 2.0 Declarative ORM & Alembic Migrations
* **AI Pipeline:** TensorFlow/Keras (MobileNetV2 9-class Defect Classifier) + OpenCV & Scikit-learn (Material Estimation & CV Feature Extraction)
* **Image Processing:** OpenCV (`cv2`) & Pillow
* **Deployment:** Unified Docker Compose (PostgreSQL, FastAPI Backend, React/Nginx Frontend)

---

## 1. Component-by-Component Mapping Matrix

| Source Repository | Existing File / Module | Proposed Destination in Target Project | Action | Detailed Engineering Rationale |
|---|---|---|---|---|
| **Primary (FastAPI)** | `frontend/src/App.jsx` & routing | `frontend/src/App.jsx` | **ADAPT** | Strong structure for protected routing and layout. Needs updating to integrate defect analysis views and fixed state propagation. |
| **Primary (FastAPI)** | `frontend/src/api.js` | `frontend/src/services/api.js` | **ADAPT** | Retain Axios interceptor for JWT refresh tokens. Enhance error handling and configure dynamic base URL via Vite environment variables (`VITE_API_URL`). |
| **Primary (FastAPI)** | `frontend/src/pages/Dashboard.jsx` & `RoleDashboards.jsx` | `frontend/src/pages/Dashboard.jsx` | **ADAPT** | Clean role-based dashboards (Admin, Facility Operator, Sustainability Manager, Manufacturer). Enhance with defect distribution graphs from Secondary. |
| **Primary (FastAPI)** | `frontend/src/pages/Inventory.jsx` | `frontend/src/pages/Inventory.jsx` | **ADAPT** | Comprehensive inventory UI with batch creation, editing, and deletion. Retain layout and connect to clean ORM API. |
| **Primary (FastAPI)** | `frontend/src/pages/UploadWaste.jsx` | `frontend/src/pages/UploadWaste.jsx` | **REWRITE** | UI is aesthetically appealing, but has a critical race-condition flaw (fetches `/history` to guess analysis IDs). Rewrite to consume backend-returned analysis IDs directly and render both material estimate AND deep learning defect predictions. |
| **Primary (FastAPI)** | `frontend/src/pages/History.jsx` | `frontend/src/pages/History.jsx` | **ADAPT** | Solid tabular view. Needs pagination, defect badge columns, and direct single/batch PDF export triggers. |
| **Primary (FastAPI)** | `frontend/src/pages/Reports.jsx` | `frontend/src/pages/Reports.jsx` | **ADAPT** | Multi-category reporting views. Connect to clean filtered export endpoints. |
| **Primary (FastAPI)** | `frontend/src/pages/Sustainability.jsx` | `frontend/src/pages/Sustainability.jsx` | **ADAPT** | Excellent sustainability metrics, trend charts, and industry benchmarking visualization. |
| **Primary (FastAPI)** | `frontend/src/components/NotificationBell.jsx` | `frontend/src/components/NotificationBell.jsx` | **ADAPT** | Functional bell notification with unread count and popover list. Retain and wire to WebSocket or polling notifications. |
| **Primary (FastAPI)** | `backend/app/main.py` | `backend/app/main.py` + `backend/app/routers/*` | **REWRITE** | Decompose 919-line monolithic router into clean FastAPI `APIRouter` modules (`routers/auth.py`, `routers/analysis.py`, `routers/inventory.py`, `routers/reports.py`, `routers/dashboards.py`). |
| **Primary (FastAPI)** | `backend/app/database.py` | `backend/app/core/database.py` & `backend/app/models/*` | **REPLACE** | Replace raw SQL string queries and dual SQLite/PostgreSQL branching with modern SQLAlchemy 2.0 Declarative Base ORM models and Alembic migrations. |
| **Primary (FastAPI)** | `backend/app/auth.py` | `backend/app/core/auth.py` | **REWRITE** | Fix critical security flaws: enforce whitelisted roles, prevent self-assigned admin registration, implement real refresh token revocation validation against the database, and remove hardcoded fallback secrets. |
| **Primary (FastAPI)** | `backend/app/cv_analysis.py` | `backend/app/services/cv_analysis.py` | **ADAPT** | Retain OpenCV GLCM texture analysis, color analysis, and contour/HSV detection. Clean up heuristic code and return structured dataclasses/Pydantic models. |
| **Primary (FastAPI)** | `backend/app/material_classifier.py` | `backend/app/services/material_classifier.py` | **ADAPT** | Keep the feature-based XGBoost pipeline structure, but clearly label its output as an **"RGB Visual Estimate"**, not a laboratory fiber test. Integrate training checkpoints when datasets are provided. |
| **Primary (FastAPI)** | `backend/app/scoring.py` | `backend/app/services/scoring.py` | **ADAPT** | Retain multi-criteria circularity scoring formula and recycling decision trees. Update rules to ingest AI-detected defect classifications from Secondary model. |
| **Primary (FastAPI)** | `backend/app/mongo.py` | `backend/app/core/document_store.py` | **REPLACE** | Replace separate MongoDB dependency with PostgreSQL native `JSONB` columns in the `analyses` table, eliminating architectural dual-database complexity while preserving raw CV payload storage. |
| **Primary (FastAPI)** | `backend/app/notifications.py` | `backend/app/services/notifications.py` | **ADAPT** | Retain business logic generating alerts for high-value recycling, hazardous materials, and milestones. Rewrite database writes to use SQLAlchemy ORM session. |
| **Primary (FastAPI)** | `backend/scripts/train_material_classifier.py` | `ml/scripts/train_material_classifier.py` | **RETAIN** | Clean training script for hand-crafted feature XGBoost classifier. Keep for reproducible training when the Ten Fabrics Dataset is available. |
| **Primary (FastAPI)** | `backend/tests/test_api.py` | `backend/tests/test_api.py` | **ADAPT** | Retain Pytest suite and expand with test cases for defect inference, role restrictions, and token revocation. |
| **Primary (FastAPI)** | `docker-compose.yml` | `docker-compose.yml` | **ADAPT** | Update to orchestrate PostgreSQL 16, FastAPI backend, and React/Nginx frontend. Remove standalone MongoDB container in favor of PostgreSQL JSONB. |
| **Secondary (Flask)** | `backend/ai/textile_model.keras` & `model/fabric_defect_model.keras` | `backend/app/ml_models/fabric_defect_model.keras` | **RETAIN** | Transfer trained 9-class MobileNetV2 defect detection weights into target repository under explicit defect detection naming. |
| **Secondary (Flask)** | `backend/ai/label_encoder.pkl` | `backend/app/ml_models/defect_labels.json` | **REPLACE** | Replace unsafe Python joblib pickle with a secure, human-readable JSON class map `{"0": "Broken stitch", ..., "8": "stain"}`. |
| **Secondary (Flask)** | `Fabric_Defect_Training.ipynb` | `ml/notebooks/Fabric_Defect_Training.ipynb` | **RETAIN** | Keep notebook as historical documentation of MobileNetV2 defect training hyperparameters and baseline accuracy metrics. |
| **Secondary (Flask)** | `backend/routes/predict.py` | `backend/app/services/defect_detector.py` | **REWRITE** | Extract TensorFlow inference logic into an async-compatible singleton service with OpenCV preprocessing, tensor batching, and confidence calibration. |
| **Secondary (Flask)** | `backend/ai/recommendations.py` | `backend/app/services/recommendations.py` | **ADAPT** | Extract specific defect-based repair actions (e.g., repairing stitch vs patching hole) and merge into Primary's comprehensive recycling decision engine. |
| **Secondary (Flask)** | `backend/services/email_service.py` | `backend/app/services/email_service.py` | **ADAPT** | Adapt SMTP report email functionality with background tasks (`BackgroundTasks` in FastAPI) and rate-limiting. |
| **Secondary (Flask)** | `best_model.keras` | N/A | **DO NOT USE** | Deprecated 20-class garment model; superseded by the 9-class defect model. |
| **Secondary (Flask)** | `notebooks/Milestone2_Data_Preprocessing.ipynb` | N/A | **DO NOT USE** | Incomplete notebook with 44k missing images. |
| **Secondary (Flask)** | `backend/app.py` & Flask routes | N/A | **DO NOT USE** | Redundant and insecure (contains plaintext passwords and unauthenticated endpoints). Primary FastAPI architecture will be used exclusively. |
| **Secondary (Flask)** | `backend/models/*` (Flask-SQLAlchemy) | N/A | **DO NOT USE** | Replaced by single SQLAlchemy 2.0 ORM model definitions. |
| **Secondary (Flask)** | `frontend/` (React 19 + Tailwind 4) | N/A | **DO NOT USE** | Duplicate frontend. Primary React 18 frontend is more feature-complete, mature, and stable. |

---

## 2. Consolidation Rationale

1. **Single Backend:** Python + FastAPI provides superior asynchronous concurrency, automatic OpenAPI/Swagger documentation, native Pydantic validation, and seamless integration with both OpenCV and TensorFlow.
2. **Single Database:** PostgreSQL 16 handles relational data (users, inventory, analyses, audit logs) and semi-structured documents (via high-performance `JSONB`), completely removing the operational complexity of managing MongoDB or SQLite fallbacks in production.
3. **Single Frontend:** Primary's React SPA has comprehensive navigation, role dashboards, and working CSS components. Secondary's frontend is an incomplete duplicate.
4. **AI Separation of Concerns:**
   - **Material Composition:** Handled by CV feature analysis / XGBoost (clearly identified as a visual surface estimate).
   - **Fabric Defect Detection:** Handled by Secondary's 9-class MobileNetV2 CNN.
   - **Sustainability & Scoring:** Handled by the unified decision engine synthesizing material, defects, and contamination.
