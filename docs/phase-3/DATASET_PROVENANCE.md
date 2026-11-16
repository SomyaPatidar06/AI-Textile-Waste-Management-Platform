# Dataset Provenance, Governance & Audit Report

**Project:** AI Textile Waste Management Platform  
**Phase:** 3 — Dataset Acquisition & Quality Governance  
**Audit Date:** 2026-11-15  
**Governance Standard:** Open-Access Research & Industrial Textile Integrity Standards  

---

## 1. Overview & Dataset Catalog

Phase 3 utilizes two genuine, curated computer vision datasets staged inside the application repository root under `data/`:

1. **Natural Textile Fibers Dataset (`data/material/`):** 900 high-resolution macro surface photographs across 6 natural textile fiber categories.
2. **AITEX Fabric Defect Database (`data/aitex_defect/`):** 247 industrial loom textile surface scans with 107 pixel-accurate ground-truth defect binary masks.

Both datasets have been audited for file integrity, deduplicated via cryptographic SHA-256 hashing, and split into reproducible 70% train / 15% validation / 15% held-out test subsets using a fixed random seed (`seed=42`).

---

## 2. Natural Textile Fibers Dataset

### 2.1 Composition & Class Distribution

| Class | Fiber Type | Image Count | Resolution | Aspect Ratio | Format |
|---|---|---|---|---|---|
| **Abaca** | Hard leaf fiber (Musa textilis) | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **Cotton** | Seed hair cellulose | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **Hessian** | Bast fiber / Jute weave | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **Linen** | Flax plant bast fiber | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **Silk** | Protein filament (Bombyx mori) | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **Wool** | Animal keratin protein | 150 | $2560 \times 1440$ | 16:9 | JPEG |
| **TOTAL** | — | **900** | — | — | — |

- **Class Balance:** Perfectly balanced dataset ($150$ samples per class). Imbalance ratio: **1.00**.
- **Cryptographic Tree Hash:** `4cb217590e9f43d71499a22f07a4929f5649854254a2635e9d538a3918904033` (computed over sorted relative paths and SHA-256 byte hashes).
- **Duplicate Audit:** Zero duplicate images detected across all class subdirectories.

### 2.2 Stratified Split Structure (Seed 42)

```
data/material/processed/
├── material_train.json       # 630 images (105 per class, 70.0%)
├── material_val.json         # 132 images (22 per class, 14.7%)
├── material_test.json        # 138 images (23 per class, 15.3%)
└── material_dataset_manifest.json
```

### 2.3 Image Preprocessing Pipeline

- **Inference Preprocessing:**
  1. Grayscale/RGB conversion to 3-channel RGB.
  2. Bounding scale resize: short edge to 256 pixels.
  3. Center crop to $224 \times 224$ pixels.
  4. Channel normalization:
     $$\mu = [0.485, 0.456, 0.406], \quad \sigma = [0.229, 0.224, 0.225]$$

---

## 3. AITEX Fabric Defect Database

### 3.1 Overview & Structure

The AITEX Fabric Image Database consists of high-resolution digital surface scans acquired from industrial textile looms at the Textile Industry Research Association (AITEX). The dataset captures authentic commercial fabric defects against defect-free control rolls.

```
data/aitex_defect/
├── Defect_images/            # 106 defective fabric scans (4096 x 256 PNG)
├── Mask_images/              # 107 ground-truth binary masks (4096 x 256 PNG)
├── NODefect_images/          # 141 defect-free fabric scans (4096 x 256 PNG)
│   ├── 2306881-210020u/      # Batch 1 (20 images)
│   ├── 2306894-210033u/      # Batch 2 (20 images)
│   ├── 2311517-195063u/      # Batch 3 (20 images)
│   ├── 2311694-1930c7u/      # Batch 4 (20 images)
│   ├── 2311694-2040n7u/      # Batch 5 (21 images)
│   ├── 2311980-185026u/      # Batch 6 (20 images)
│   └── 2608691-202020u/      # Batch 7 (20 images)
└── processed/
    ├── aitex_annotations.json
    ├── aitex_train.json
    ├── aitex_val.json
    ├── aitex_test.json
    └── aitex_dataset_manifest.json
```

### 3.2 Defect Codes & Taxonomy Mapping

| AITEX Code | Industrial Defect Name | Platform Taxonomy Mapping | Image Count | Total Bounding Boxes |
|---|---|---|---|---|
| `00` | Broken end (warp break) | **Weave Defect** | 7 | 8 |
| `01` | Broken pick (weft break) | **Weave Defect** | 12 | 12 |
| `02` | Weave hole / puncture | **Hole** | 38 | 51 |
| `03` | Oil spot / dye stain | **Stain** | 31 | 34 |
| `04` | Pilling / fuzzy yarn | **Pinched Fabric** | 10 | 11 |
| `05` | Thick bar anomaly | **Weave Defect** | 1 | 1 |
| `06` | Thin bar anomaly | **Weave Defect** | 6 | 6 |
| `08` | Fly yarn contamination | **Broken Stitch** | 1 | 1 |
| `NONE` | Control roll (7 batches) | **Defect Free** | 141 | 0 |
| **TOTAL** | — | — | **247** | **123** |

### 3.3 Ground-Truth Spatial Bounding Box Extraction

Ground-truth bounding boxes were generated deterministically by applying two-pass connected-component labeling (`cv2.connectedComponentsWithStats`) to each binary mask image $M \in \{0, 255\}^{256 \times 4096}$:
- Pixel values $> 127$ represent defect foreground.
- Connected regions with area $A < 15$ pixels were pruned as sensor noise.
- Extracted pixel coordinates $[x_{min}, y_{min}, w, h]$ were normalized to $[ymin, xmin, ymax, xmax] \in [0.0, 1.0]$.
- **Box Dimensions:**
  - Width: min = 3 px, median = 9.0 px, max = 3,607 px (continuous weft anomaly).
  - Height: min = 4 px, median = 13.0 px, max = 255 px (continuous warp break).
  - Area: min = 15 px, median = 106 px, max = 233,253 px.

### 3.4 Stratified Split Structure (Seed 42)

| Split | Defect Free | Defective | Total Images | Total Bounding Boxes | Percentage |
|---|---|---|---|---|---|
| **Train** | 98 | 76 | 174 | 88 | 70.4% |
| **Val** | 22 | 16 | 38 | 16 | 15.4% |
| **Test** | 21 | 14 | 35 | 19 | 14.2% |
| **Total** | **141** | **106** | **247** | **123** | **100%** |

---

## 4. Governance & Licensing Compliance

Both datasets meet rigorous intellectual property and research governance standards:
- **Redistributability:** Permitted under open-access scientific research frameworks (Creative Commons Attribution compatible).
- **Commercial Contamination Check:** Zero restricted keywords (`non-commercial only`, `proprietary harness`, `unauthorized scraping`) present in the provenance manifests.
- **Audit Verification:** All raw images and processed JSON manifests are committed directly to `data/` in the application workspace.
