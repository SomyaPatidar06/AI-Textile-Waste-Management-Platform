# Workspace Inventory and Static Verification Report

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `https://github.com/SomyaPatidar06/AI-Textile-Waste-Management-Platform`  
**Audit Timestamp:** 2026-11-15T10:45:00+05:30  
**Audit Mode:** Read-Only Static Verification (Phase 1)

---

## 1. Executive Summary of Workspace Inspection

The initial workspace inspection evaluated the physical file system structure of `D:\Textile-Waste-Workspace` against the expected repository structure specified in the project charter.

### Discrepancy & Verification Findings

| Expected Path / Resource | Physical Disk Path / Status | Status Classification | Details |
|---|---|---|---|
| `AI-Textile-Waste-Management-Platform/` | `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform` | **CLONED ON-DEMAND** | Initially missing on disk. Cloned from `https://github.com/SomyaPatidar06/AI-Textile-Waste-Management-Platform`. Verified empty repository on branch `main` (0 commits, clean working tree). |
| `reference-repositories/primary-srilakshmi/` | `D:\Textile-Waste-Workspace\reference-repositories\textile-waste-intelligence-platform-main` | **NAME VARIATION (EXTRACTED ZIP)** | Folder extracted directly from GitHub ZIP archive `textile-waste-intelligence-platform-main`. Does not contain a `.git` metadata directory. |
| `reference-repositories/secondary-thanmayee/` | `D:\Textile-Waste-Workspace\reference-repositories\Textile-Waste-management-platform-main` | **NAME VARIATION (EXTRACTED ZIP)** | Folder extracted directly from GitHub ZIP archive `Textile-Waste-management-platform-main`. Does not contain a `.git` metadata directory. |

---

## 2. Directory Tree Layouts

### 2.1 Primary Reference Repository
* **Source:** https://github.com/Srilakshmi-33kommu/textile-waste-intelligence-platform
* **Disk Root:** `D:\Textile-Waste-Workspace\reference-repositories\textile-waste-intelligence-platform-main`
* **File Count:** 47 files across 9 directories.

```text
textile-waste-intelligence-platform-main/
├── .gitignore
├── docker-compose.yml
├── LICENSE
├── PROJECT_README.md
├── README.md
├── backend/
│   ├── Dockerfile
│   ├── README.md
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── cv_analysis.py
│   │   ├── database.py
│   │   ├── features.py
│   │   ├── main.py
│   │   ├── material_classifier.py
│   │   ├── mongo.py
│   │   ├── notifications.py
│   │   ├── schemas.py
│   │   └── scoring.py
│   ├── scripts/
│   │   └── train_material_classifier.py
│   └── tests/
│       └── test_api.py
└── frontend/
    ├── Dockerfile
    ├── index.html
    ├── package.json
    ├── package-lock.json
    ├── postcss.config.js
    ├── tailwind.config.js
    ├── vite.config.js
    └── src/
        ├── App.jsx
        ├── api.js
        ├── main.jsx
        ├── styles.css
        ├── components/
        │   ├── AdminDashboard.jsx
        │   ├── NotificationBell.jsx
        │   ├── RoleDashboards.jsx
        │   ├── Sidebar.jsx
        │   └── ui.jsx
        └── pages/
            ├── Dashboard.jsx
            ├── History.jsx
            ├── Inventory.jsx
            ├── Login.jsx
            ├── Profile.jsx
            ├── Register.jsx
            ├── Reports.jsx
            ├── Settings.jsx
            ├── Sustainability.jsx
            └── UploadWaste.jsx
```

### 2.2 Secondary Reference Repository
* **Source:** https://github.com/Thanmayeenadimpalli/Textile-Waste-management-platform
* **Disk Root:** `D:\Textile-Waste-Workspace\reference-repositories\Textile-Waste-management-platform-main`
* **Key Artifacts:** Pretrained weights (`best_model.keras`, `textile_model.keras`, `fabric_defect_model.keras`), training notebooks, test images, Flask backend, and React frontend.

```text
Textile-Waste-management-platform-main/
├── .gitignore
├── best_model.keras                         (9,927,761 bytes - Keras 3 format, 20 classes)
├── Fabric_Defect_Training.ipynb             (1,732,909 bytes - Complete executed notebook)
├── LICENSE
├── package.json
├── package-lock.json
├── README.md
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── ai/
│   │   ├── label_encoder.pkl                (Joblib pickle - 9 defect classes)
│   │   ├── recommendations.py               (Rule-based recycling recommendations)
│   │   ├── sustainability.py                (Sustainability and circularity scoring)
│   │   └── textile_model.keras              (11,607,152 bytes - MobileNetV2 9-class defect model)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── inventory.py
│   │   ├── notification.py
│   │   ├── prediction.py
│   │   └── user.py
│   ├── routes/
│   │   ├── auth.py                          (Plaintext password vulnerability)
│   │   ├── circularity.py
│   │   ├── dashboard.py
│   │   ├── history.py
│   │   ├── inventory.py
│   │   ├── notifications.py
│   │   ├── predict.py                       (Image inference endpoint)
│   │   ├── recommendations.py
│   │   ├── reports.py
│   │   └── sustainability.py
│   ├── services/
│   │   ├── email_service.py
│   │   └── notification_service.py
│   ├── tests/
│   │   └── test_api.py
│   └── uploads/                             (16 sample test and demonstration images)
├── model/
│   └── fabric_defect_model.keras            (11,607,152 bytes - Identical to textile_model.keras)
├── notebooks/
│   ├── Fabric_Defect_Training.ipynb         (0 bytes - Empty placeholder)
│   ├── Milestone2_Data_Preprocessing.ipynb  (6,802 bytes - styles.csv exploration)
│   └── Model_Training.ipynb                 (0 bytes - Empty placeholder)
├── test_images/                             (3 sample evaluation images)
└── frontend/                                (React 19 + Tailwind v4 + Vite SPA)
```

---

## 3. Physical Checksum and Binary Asset Verification

Static SHA-256 verification of large binary model assets in secondary repository:

| File Path | Size (Bytes) | SHA-256 Checksum | Detected Architecture |
|---|---|---|---|
| `best_model.keras` | 9,927,761 | `e9dc1db3832c1f8eeadac2a376562da76cfae4fc76fb6c578f2f30d3f4241a05` | Keras 3 Functional, MobileNetV2 base, 20 output units (Softmax) |
| `backend/ai/textile_model.keras` | 11,607,152 | `5630bddef1006df7f82602b149e42609f086f610c9a09628cc4938e1494e801e` | Keras 3 Functional, MobileNetV2 base, 9 output units (Softmax) |
| `model/fabric_defect_model.keras` | 11,607,152 | `5630bddef1006df7f82602b149e42609f086f610c9a09628cc4938e1494e801e` | **Exact duplicate** of `textile_model.keras` |
| `backend/ai/label_encoder.pkl` | 741 | `c84381014e7ce292bbfb77c5bba3f08034dbf7b7cb27a003fdb0000a624fe461` | Scikit-learn `LabelEncoder` containing 9 fabric defect classes |

---

## 4. Target Repository Git Verification

The target repository was cloned via HTTPS:
* Remote URL: `https://github.com/SomyaPatidar06/AI-Textile-Waste-Management-Platform`
* Local Path: `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`
* Current Branch: `main`
* Working Tree Status: Initialized, clean, 0 commits present.
* Git configuration: Tracking `origin/main`.
