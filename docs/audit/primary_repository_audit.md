# Primary Repository Source Audit: Srilakshmi Intelligence Platform

**Reference Path:** `reference-repositories/textile-waste-intelligence-platform-main`  
**GitHub:** `https://github.com/Srilakshmi-33kommu/textile-waste-intelligence-platform`  
**Stack Identified:** FastAPI 0.111.0, SQLAlchemy 2.0 (Raw Core Queries), React 18.3.1, Tailwind CSS 3.4.4, Vite 5.3.3, OpenCV 4.10, Scikit-learn, ReportLab 4.2.0, PostgreSQL 16 + SQLite Fallback, MongoDB 7.

---

## 1. Feature Classification Matrix

| Feature Module | Source File Reference | Classification Status | Source Code Evidence & Analysis |
|---|---|---|---|
| **1. Frontend Architecture** | `frontend/src/App.jsx`, `frontend/src/api.js` | **Implemented and verified** | Clean React 18 SPA using React Router DOM v6, Axios interceptor with token refresh handling, responsive Tailwind layout, and reusable UI components (`components/ui.jsx`). |
| **2. Backend Architecture** | `backend/app/main.py` | **Implemented and verified** | FastAPI application with modular helper imports (`auth.py`, `cv_analysis.py`, `scoring.py`, `mongo.py`, `notifications.py`). Monolithic route file (`main.py` has 919 lines). |
| **3. FastAPI Endpoints** | `backend/app/main.py` | **Implemented and verified** | 22 REST endpoints covering auth, admin, dashboards, inventory, analysis, history, reports, exports, and notifications. |
| **4. Database Schema & ORM** | `backend/app/database.py` (lines 59-130) | **Partially implemented / Broken compatibility** | Tables defined via raw SQL DDL strings (`PG_SCHEMA` & `SQLITE_SCHEMA`). No declarative SQLAlchemy ORM classes (`Base = declarative_base()`). PostgreSQL/SQLite compatibility bugs exist (e.g., boolean types vs integers). |
| **5. Authentication & Authorization** | `backend/app/auth.py`, `main.py` (lines 57-157) | **Broken / Critical Security Flaw** | Uses `passlib[bcrypt]` and JWT (`python-jose`). However, public registration permits registering directly as `"admin"` role, and refresh token revocation is bypassed in `/api/auth/refresh`. |
| **6. Inventory Functionality** | `backend/app/main.py` (lines 391-440), `frontend/src/pages/Inventory.jsx` | **Implemented and verified** | Full CRUD implemented (List, Create, Update, Delete) with batch validation and role enforcement (`admin`, `manufacturer`, `recycling_operator`). |
| **7. Image Upload & Preprocessing** | `backend/app/main.py` (lines 443-590), `backend/app/cv_analysis.py` | **Implemented and verified** | Uploads processed via `FastAPI.UploadFile`, converted to OpenCV BGR arrays via `cv2.imdecode(np.frombuffer(...))`. Batch up to 5 images supported. |
| **8. Material Classification** | `backend/app/material_classifier.py` | **Placeholder or hardcoded** | Model files `material_model.joblib` and `material_labels.json` **do not exist** on disk. Inference always executes `_rule_based_classify` using hardcoded color/texture thresholds and synthetic confidence numbers (e.g., 78.5% for denim). |
| **9. Defect Detection** | `backend/app/cv_analysis.py` (lines 126-174) | **Placeholder / Rule-based heuristic** | No deep learning or object detection model. Employs OpenCV Canny edge contour area thresholds (`damage_pct = (damage_area / total_area) * 100`). |
| **10. Quality Assessment** | `backend/app/cv_analysis.py` (lines 73-124) | **Implemented and verified (CV Heuristics)** | GLCM texture features (contrast, homogeneity, energy, smoothness) combined with 2D FFT spectral regularity to output texture quality ratings (`GOOD`, `AVERAGE`, `POOR`). |
| **11. Recycling Recommendations** | `backend/app/scoring.py` (lines 102-176) | **Implemented and verified (Deterministic Engine)** | Decision rules mapping classified material, condition, and circularity score to 7 recycling pathways (Fiber Recycling, Mechanical, Chemical, Reuse, Upcycling, Donation, Industrial Recovery). |
| **12. Sustainability Calculations** | `backend/app/scoring.py` (lines 178-234) | **Implemented and verified (Formula-based)** | Multi-factor circularity formula: Recyclability (35%), Condition (20%), Reuse (20%), Environmental (15%), Feasibility (10%). Estimates carbon ($4.2 \text{ kg CO}_2 / 100\text{ score}$) and water ($2650 \text{ L} / 100\text{ score}$) savings. |
| **13. Analytics and Reporting** | `backend/app/main.py` (lines 601-710, 713-865) | **Implemented and verified** | ReportLab PDF stream generation (single item, batch, and sustainability), OpenPyXL Excel export, CSV export, and role-specific dashboard metrics. |
| **14. Docker & Deployment** | `docker-compose.yml`, `backend/Dockerfile`, `frontend/Dockerfile` | **Partially implemented** | Compose configuration defines 4 services: backend, frontend, postgres (16-alpine), and mongo (7). Container setup is structured but not validated in production environment. |
| **15. Existing Tests** | `backend/tests/test_api.py` | **Implemented and verified** | 12 Pytest integration tests using `starlette.testclient.TestClient`. Tests verify health, auth, role enforcement, inventory CRUD, and report generation. |
| **16. Dependencies & Compatibility** | `backend/requirements.txt`, `frontend/package.json` | **Implemented and verified** | Requirements are modern and pinned (FastAPI 0.111.0, Pydantic 2.9+, SQLAlchemy 2.0.31, Psycopg v3, OpenCV 4.10.0, Vite 5.3, React 18.3). |
| **17. Environment Configuration** | `backend/app/database.py`, `backend/app/auth.py` | **Partially implemented / Unsafe Defaults** | Relies on `os.environ.get()` with hardcoded development fallbacks for database URLs and JWT secrets. |

---

## 2. In-Depth Subsystem Technical Analysis

### 2.1 Backend Architecture & Routing (`backend/app/main.py`)
The backend is structured around a single monolithic routing script:
* **Startup Initialization:** Lines 45-50 run `init_db()` which executes multi-statement DDL on PostgreSQL or local SQLite.
* **CORS Middleware:** Lines 36-42 configure:
  ```python
  app.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  ```
  *Security Issue:* `allow_origins=["*"]` with `allow_credentials=True` violates the CORS specification in all modern browsers and poses CSRF/cross-origin leak vulnerabilities.
* **Endpoint Inventory:**
  - Auth: `POST /api/auth/register`, `POST /api/auth/login`, `POST /api/auth/token`, `POST /api/auth/refresh`, `POST /api/auth/logout`, `GET/PUT /api/auth/profile`, `DELETE /api/auth/account`, `POST /api/auth/change-password`
  - Admin: `GET /api/admin/users`, `PUT /api/admin/users/{user_id}/role`, `DELETE /api/admin/users/{user_id}`, `GET /api/dashboard/admin`
  - Role Dashboards: `GET /api/dashboard/recycling-facility`, `GET /api/dashboard/sustainability-manager`, `GET /api/dashboard/manufacturer`, `GET /api/dashboard/summary`
  - Inventory: `GET /api/inventory`, `POST /api/inventory`, `PUT /api/inventory/{item_id}`, `DELETE /api/inventory/{item_id}`
  - Analysis: `POST /api/analyze`, `POST /api/analyze-batch`, `GET /api/history`
  - Reports & Exports: `GET /api/reports`, `GET /api/reports/summary`, `GET /api/reports/export/excel`, `GET /api/reports/export/csv`, `GET /api/report/{id}/pdf`, `GET /api/report/batch/pdf`, `GET /api/sustainability/report/pdf`
  - Notifications: `GET /api/notifications`, `GET /api/notifications/unread-count`, `PUT /api/notifications/{id}/read`, `PUT /api/notifications/mark-all-read`, `DELETE /api/notifications/{id}`
  - Settings: `GET /api/settings`, `PUT /api/settings`

### 2.2 Database Layer & Schema (`backend/app/database.py`)
* **Dual Database Strategy:** Uses `_build_engine()` to test PostgreSQL connection string `DATABASE_URL`. If connection fails (e.g., Docker down), it catches the exception and falls back to `sqlite:///textile_waste_fallback.db`.
* **Execution Pattern:** All queries bypass SQLAlchemy ORM declarative models, executing raw SQL with parameter bindings:
  ```python
  with db_session() as conn:
      row = conn.execute(text("SELECT ... WHERE email=:e"), {"e": email}).mappings().first()
  ```
* **PostgreSQL / SQLite Incompatibilities:**
  1. In `main.py` line 111 (`logout`): `UPDATE refresh_tokens SET revoked=1 WHERE token=:t`. In PostgreSQL, `revoked` is a `BOOLEAN DEFAULT FALSE`. Assigning integer `1` raises a strict type error in PostgreSQL unless explicitly cast.
  2. In `main.py` lines 345 & 354: Query strings branch with `if not USING_POSTGRES: " AND is_read=0"` else `" AND is_read=FALSE"`.
  3. Dynamic string construction in update queries (`main.py` line 133):
     ```python
     set_clause = ", ".join([f"{k}=:{k}" for k in fields])
     conn.execute(text(f"UPDATE users SET {set_clause} WHERE id=:id"), {**fields, "id": user["id"]})
     ```
     While parameter values are bound, column identifiers are interpolated dynamically into SQL statements without validation against a column whitelist.

### 2.3 Computer Vision & Material Classification Pipeline (`material_classifier.py` & `cv_analysis.py`)
* **Material Classifier Reality:**
  - Script `backend/scripts/train_material_classifier.py` defines an XGBoost pipeline utilizing 40 hand-crafted features: 16 HSV Hue bins, 8 Saturation bins, 8 Value bins, 5 GLCM texture properties (contrast, homogeneity, energy, correlation, dissimilarity), Canny edge density, mean grayscale, and standard deviation.
  - However, the binary weights file `material_model.joblib` and metadata `material_labels.json` **do not exist**.
  - As a result, `_try_load_model()` fails silently and routes every inference request to `_rule_based_classify(img, color_result, texture_result)`:
    ```python
    is_blue_dark = b > r and b > 60 and (r + g + b) < 420
    if is_blue_dark and roughness > 35:
        return "Denim", 78.5
    if smoothness > 78 and uniformity > 75 and saturation > 40:
        return "Silk", 74.0
    ...
    ```
  - This is a non-machine-learning rule heuristic with hardcoded pseudo-confidence numbers.
* **Damage and Contamination Detection:**
  - Damage detection in `cv_analysis.py` lines 126-174 applies Canny edge detection (`cv2.Canny(gray, 50, 150)`) and computes contour area sums. It does not identify defect categories (e.g., tears vs needle marks vs stitching defects).
  - Contamination detection in `cv_analysis.py` lines 177-221 uses HSV threshold masks for dark pixels (oil), desaturated high-value pixels (dust), and hue dispersion (chemicals).

### 2.4 Frontend Architecture & UI Flaws
* Built with Vite 5 and React 18, utilizing Tailwind CSS for styling.
* Routes and layouts are cleanly separated with role-based dashboard rendering in `RoleDashboards.jsx` (Admin, Manufacturer, Sustainability Manager, Recycling Operator).
* **Upload Tracking Defect (`UploadWaste.jsx` lines 55-57):**
  When uploading batch images to `/api/analyze-batch`, the backend does not return the generated database IDs of the inserted analyses. The frontend executes a race-prone secondary call:
  ```javascript
  const hist = await api.get('/history')
  const ids = (hist.data || []).slice(0, data.results.length).map((r) => r.id)
  setAnalysisIds(ids.reverse())
  ```
  If another user submits an analysis in the same millisecond window, the wrong PDF report IDs will be linked in the UI.

---

## 3. Summary of Strengths and Critical Deficiencies

### Strengths
1. Rich, cohesive domain model combining circularity scoring, recycling recommendations, ESG sustainability benchmarks, and PDF/Excel reporting.
2. Complete, working React frontend with dark theme, responsive navigation, and role-based views.
3. Clean separation of concerns between CV feature extraction and multi-criteria scoring logic.
4. Comprehensive ReportLab PDF generator producing professional analysis certificates and sustainability reports.

### Critical Deficiencies
1. **No trained material classifier weights:** Relies entirely on color/texture rule heuristics.
2. **No deep learning defect detection:** Uses primitive contour area calculations.
3. **Severe authentication vulnerabilities:** Unrestricted admin registration and bypassed refresh token revocation.
4. **Fragile database layer:** Raw SQL strings, lack of Alembic migrations, and PostgreSQL/SQLite type friction.
5. **CORS policy violation:** Insecure configuration (`allow_origins=["*"]` with `allow_credentials=True`).
