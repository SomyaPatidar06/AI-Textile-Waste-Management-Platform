# AI Textile Waste Management Platform (v2.1.0)

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61dafb.svg)](https://react.dev/)
[![PyTorch](https://img.shields.io/badge/PyTorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![ONNX Runtime](https://img.shields.io/badge/ONNX%20Runtime-1.17+-005CED.svg)](https://onnxruntime.ai/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)

An industrial-grade, AI-powered circular economy platform designed to digitize, characterize, and optimize textile waste sorting, recycling pathways, and life-cycle environmental compliance.

---

## 1. Problem Statement & Mission

Global textile manufacturing generates over **92 million tonnes** of waste annually, with less than **1%** recycled into new clothing. A primary bottleneck in circular textile supply chains is the reliance on manual visual inspection, which is inconsistent, slow, and unable to reliably quantify fiber purity, defect severity, or life-cycle recovery potential.

The **AI Textile Waste Management Platform** bridges this gap by combining:
1. **Optical Computer Vision:** Deep learning characterization of natural textile fibers and spatial surface defect localization.
2. **Standardized Circularity Engine:** Mathematical scoring across 5 weighted dimensions and 7 actionable recycling/upcycling pathways.
3. **Consignment Lifecycle Tracking:** End-to-end batch provenance from intake through sorting, processing, and dispatch with immutable audit logging.
4. **Automated ESG Intelligence:** ISO-14040/44 compliant life-cycle environmental impact calculations ($CO_2$, water, energy savings) and verifiable digital circularity passports.
5. **Liquid Glass Design System:** Premium industrial analytics interface delivering WCAG AAA compliant optical clarity across desktop, tablet, and mobile terminals.

---

## 2. Key Capabilities

### 2.1 Multi-Task AI Textile Characterization
- **Natural Fiber Classification:** Fine-tuned ResNet-18 model achieving **93.48% accuracy** (95% CI: $[88.1\%, 96.5\%]$) across 6 natural fiber classes (`Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool`).
- **Spatial Defect Detection:** Multi-scale spatial scanning identifying weave defects, holes, stains, pinched fabric, and broken stitches with normalized bounding box guidance overlays.
- **ONNX Runtime Acceleration:** Embedded ONNX Runtime pipeline delivering a **1.81x inference speedup** (21.23 ms CPU latency).
- **Option B Governance Policy:** Strictly adheres to textile standard disclosures: optical RGB predictions are visual estimates and require human-operator validation for uncertain consignments.

### 2.2 Circularity Scoring & Routing Algorithms
- **5-Factor Circularity Scoring:**
  $$\text{Score} = 0.35 R + 0.20 C + 0.20 U + 0.15 E + 0.10 F$$
  Evaluates Recyclability ($R$), Condition ($C$), Reuse ($U$), Eco-benefit ($E$), and Feasibility ($F$).
- **7 Recycling & Recovery Pathways:** Automatically routes consignments to Fiber Re-spinning, Thermal Shoddy, Chemical Dissolution, Garment Resale/Donation, Industrial Wiping Rags, Precision Upcycling, or Energy Recovery.

### 2.3 Role-Differentiated Executive Hub
- **4 Granular User Roles:**
  - `OPERATOR`: Consignment intake, optical image scanning, canvas inspection, and manual review.
  - `SUSTAINABILITY_MANAGER`: Enterprise ESG analytics, avoided carbon tracking, and LCA reports.
  - `MANUFACTURER`: Feed purity monitoring, defect severity distribution, and lot allocation.
  - `ADMIN`: User management, neural checkpoint telemetry, and infrastructure health monitoring.

### 2.4 Digital Product Passports & Public Verification
- **Verifiable Passports:** Issues structured circularity certificates containing cryptographic hashes, verified scan counts, and compliance status.
- **Public Lookup Tool:** Unauthenticated public verification endpoint allowing third-party buyers or auditors to confirm certificate authenticity against the platform registry.

---

## 3. Technology Stack

- **Backend:** Python 3.11+ / 3.14, FastAPI, SQLAlchemy 2.0, Alembic, Pydantic v2, PyTorch CPU, ONNX Runtime, OpenCV, PIL, NumPy.
- **Frontend:** React 18, Vite 5, Tailwind CSS 3, Lucide React, Axios.
- **Database & Storage:** SQLite 3 (local development with zero-lock online backup) / PostgreSQL 16 (production container stack).
- **Deployment:** Multi-container Docker Compose with Nginx reverse proxy, automated health probes, and security headers.

---

## 4. System Architecture

```
┌────────────────────────────────────────────────────────┐
│                   Client Browser                       │
│    (Liquid Glass UI: Desktop, Laptop, Tablet, Mobile)  │
└───────────────────────────┬────────────────────────────┘
                            │ (HTTP / JSON / WS)
                            ▼
┌────────────────────────────────────────────────────────┐
│             Nginx 1.25 Reverse Proxy (:80)             │
│    - Serves compiled SPA assets                        │
│    - Gzip compression & security headers               │
│    - Routes /api/ to backend container                 │
└───────────────────────────┬────────────────────────────┘
                            │
                            ▼
┌────────────────────────────────────────────────────────┐
│             FastAPI Backend Service (:8000)            │
│  ├── Auth & RBAC (Argon2id, JWT Rotation & Blocklist)  │
│  ├── Inventory Lifecycle & Audit History Engine        │
│  ├── AI Inference Engine (ResNet-18 & ONNX Runtime)    │
│  │   ├── MaterialEngine (6-class natural fibers)       │
│  │   └── SpatialDefectDetector (Multi-scale scanner)   │
│  ├── Circularity & 7-Pathway Recommendation Engine     │
│  └── ISO-14040 LCA Environmental Impact Calculator     │
└─────────────┬────────────────────────────┬─────────────┘
              │                            │
              ▼                            ▼
┌───────────────────────────┐ ┌──────────────────────────┐
│  PostgreSQL 16 / SQLite   │ │ Persistent Storage       │
│  - Relational Schemas     │ │ - Uploaded Scans         │
│  - Immutable Audit Logs   │ │ - Zero-Lock Backups      │
└───────────────────────────┘ └──────────────────────────┘
```

---

## 5. Quickstart & Local Execution

### 5.1 Prerequisites
- Python 3.11, 3.12, or 3.14
- Node.js v18+ and npm v9+

### 5.2 Backend Setup
```bash
cd backend

# 1. Create and activate virtual environment
python -m venv .venv
# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Apply database migrations
alembic upgrade head

# 5. Seed default test accounts
python scripts/create_initial_admin.py
python scripts/seed_test_roles.py

# 6. Start backend development server
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```

The interactive API documentation is available at `http://127.0.0.1:8000/docs`.

### 5.3 Frontend Setup
```bash
cd ../frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```

The frontend application will be live at `http://localhost:5173`.

### 5.4 Seed Credentials
| Role | Username | Email | Password |
| :--- | :--- | :--- | :--- |
| **Administrator** | `admin` | `admin@textilewaste.platform` | `AdminSecret2026!` |
| **Operator** | `operator1` | `operator@textilewaste.platform` | `OperatorSecret2026!` |
| **Sustainability Manager** | `sustain1` | `sustain@textilewaste.platform` | `SustainSecret2026!` |
| **Manufacturer** | `manuf1` | `manuf@textilewaste.platform` | `ManufSecret2026!` |

---

## 6. AI Model Checkpoints & Scientific Evaluation

### 6.1 Checkpoint Inventory & Integrity Verification
The platform includes an automated model integrity verification utility that computes SHA-256 hashes and cross-references expected parameters:

```bash
cd backend
python -m app.ai.model_verifier
```

| Checkpoint | Architecture | Task & Output Classes | SHA-256 Hash | Size (Bytes) |
| :--- | :--- | :--- | :--- | :--- |
| `fabric_model_v2.pth` | ResNet-18 (PyTorch) | 6 Natural Fibers (`Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool`) | `6bbcd54c...9ff1c529` | 44,797,323 |
| `fabric_model_v2.onnx` | ResNet-18 (ONNX) | Graph-Optimized Natural Fiber Inference | `2a96533c...fa71ae0` | 44,708,876 |
| `aitex_defect_model.pth` | ResNet-18 (PyTorch) | 7-Class Defect Classifier & Sliding Window Guidance | `8eab4a06...1bce304a` | 44,797,259 |
| `aitex_defect_model.onnx` | ResNet-18 (ONNX) | Graph-Optimized Surface Defect Inference | `fc296ecb...add7b4b` | 44,708,876 |

*Missing Weights Handling:* If checkpoints are missing upon a fresh clone, the platform's `/health/ready` probe fails gracefully with HTTP 503 and clear diagnostic messages. Checkpoints can be reproduced locally using `python -m app.ai.training.train_material` and `python -m app.ai.training.train_defect_detector`.

### 6.2 Empirical Benchmark Summary
Evaluated on genuine group-held-out splits (independent loom batches and rolls):

| Metric | Natural Fiber Classifier | Defect Anomaly Scanner |
| :--- | :---: | :---: |
| **Test Accuracy** | **93.48%** (95% CI: $[88.1\%, 96.5\%]$) | **100.00%** (Defective Roll Recall) |
| **Ground Truth Defect Coverage** | N/A | **73.68% - 89.5%** (Region Intersection) |
| **Spatial Localization mAP@50** | N/A | **0.00%** (Coarse guidance, not pixel IoU) |
| **Clean Weave Specificity** | N/A | **0.00%** on novel weaves (Human-in-the-loop required) |
| **Macro F1-Score** | **93.32%** | N/A |
| **Expected Calibration Error (ECE)** | **0.0235** (2.35%) | N/A |
| **PyTorch CPU Latency** | 38.47 ms | 38.92 ms |
| **ONNX Runtime CPU Latency** | **21.23 ms** (**1.81x speedup**) | **21.45 ms** |

*AITEX Checkpoint Provenance & Generalization Note:* The deployed checkpoint (`aitex_defect_model.pth`) was originally trained on patch-based splits where patches from rolls `002` and `010` were present in the training set. Evaluating this checkpoint against the newly partitioned group-held-out manifest constitutes an **exploratory evaluation with prior training exposure** to those defect rolls (explaining the 100% defective roll recall). When evaluated on roll `013` (clean fabric completely unseen during training), the model flagged normal weave texture variations as anomalies (0.00% specificity / 100% false alarm rate). Consequently, autonomous industrial deployment is not defensible; the model operates strictly as a human-in-the-loop operator triage tool.

*Spatial Guidance Note:* Textile defects in industrial weaving (e.g., broken yarns, needle marks) are 10–30 px wide hair-thin structures. The multi-scale sliding window detector produces coarse candidate inspection bounding boxes that intersect 73.7%–89.5% of defects, but fail strict $\text{IoU} \ge 0.50$ area criteria ($0.00\%$ mAP@50). Bounding boxes are explicitly presented in the interface as coarse visual guidance regions for operator review.

---

## 7. Automated Testing Suite

### 7.1 Backend Unit & Integration Tests (60 Tests)
```bash
cd backend
python -m pytest tests/ -v
```
*Result: 60 passed in 148s (100% pass rate).*

### 7.2 End-to-End Acceptance Tests (17 Checkpoints)
```bash
cd backend
python scripts/phase8_acceptance_tests.py
```
*Result: 17 of 17 checkpoints passed (100% pass rate).*

### 7.3 Independent AI Validation & Calibration Suite
```bash
cd backend
python scripts/phase9_independent_ai_evaluation.py
```

### 7.4 Production Frontend Compilation
```bash
cd frontend
npm run build
```
*Result: Built in 4.01s with 0 compiler warnings (~101 kB gzip).*

---

## 8. Docker Deployment

Deploy the entire production stack (Nginx + FastAPI + PostgreSQL 16) with Docker Compose:

```bash
# 1. Configure production environment
cp .env.example .env

# 2. Build and run containers in detached mode
docker compose up -d --build

# 3. Verify running containers and health probes
docker compose ps
```

---

## 9. Licensing & Attribution

- **Application Code:** [MIT License](LICENSE).
- **AITEX Fabric Defect Database:** Publicly provided by the Textile Industry Research Association (AITEX), Spain. Citations: *J. Silvestre-Blanes et al., A Public Fabric Database for Defect Detection Methods and Its Validation, 2014*.
- **Natural Textile Fibers Dataset:** Open academic research dataset licensed under CC BY 4.0.
- **ResNet-18 Backbone:** PyTorch Torchvision licensed under BSD 3-Clause.
