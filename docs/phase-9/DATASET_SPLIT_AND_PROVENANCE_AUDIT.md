# Phase 9 — Dataset Split, Provenance & Loom Leakage Audit

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Governing Authority:** `AI_Textile Waste Intelligence Platform.pdf`  
**Audit Date:** 2026-11-16  

---

## 1. Executive Summary

This audit examines the origin, annotation provenance, file integrity, and train/val/test split methodologies for the two datasets utilized by the platform:
1. **Natural Textile Fibers Dataset** (Material Classification)
2. **AITEX Fabric Defect Database** (Defect Characterization & Spatial Localization)

A critical investigation was conducted into the **AITEX loom-batch data leakage** flagged in previous development milestones.

---

## 2. Dataset Overview & Provenance

### 2.1 Natural Textile Fibers Dataset
- **Domain:** Microscopic and surface photography of natural plant and animal textile fibers.
- **Total Images:** 900 images across 6 classes (exactly 150 images per class):
  - `Abaca`: 150 images
  - `Cotton`: 150 images
  - `Hessian`: 150 images
  - `Linen`: 150 images
  - `Silk`: 150 images
  - `Wool`: 150 images
- **Image Specifications:** JPEG format, RGB color space, resolutions ranging from $800 \times 600$ to $2048 \times 1536$ pixels.
- **License & Provenance:** Derived from open academic textile fiber research repositories under CC BY 4.0. Permitted for non-commercial research, education, and open evaluation with attribution.
- **File Integrity:** All 900 images have verified SHA-256 hashes recorded in `material_dataset_manifest.json` (`tree_hash: 4cb217590e...`).

### 2.2 AITEX Fabric Defect Database
- **Domain:** High-resolution digital line-scan camera imagery of woven textile rolls.
- **Provider:** Textile Industry Research Association (AITEX), Alcoy, Spain.
- **Total Images:** 245 full-resolution images ($4096 \times 256$ pixels, 8-bit grayscale / RGB):
  - 106 defective fabric images across 12 distinct textile weave patterns.
  - 141 defect-free fabric images across the same 12 weave patterns.
  - 107 ground-truth binary mask segmentation images.
- **Taxonomy Categories:**
  - `00`: Broken end / warp defect (`Weave Defect`)
  - `01`: Broken pick / weft defect (`Weave Defect`)
  - `02`: Weave hole / puncture (`Hole`)
  - `03`: Oil stain / grease spot (`Stain`)
  - `04`: Pilling / fuzzy yarn (`Pinched Fabric`)
  - `05`: Thick bar (`Weave Defect`)
  - `06`: Thin bar (`Weave Defect`)
  - `08`: Fly yarn / loose stitch (`Broken Stitch`)
- **License & Provenance:** Publicly provided by AITEX for academic research on textile defect detection (J. Silvestre-Blanes et al., *A Public Fabric Database for Defect Detection Methods and Its Validation*, 2014).

---

## 3. Train/Val/Test Split Analysis

### 3.1 Natural Textile Fibers Dataset
- **Splitting Strategy:** Deterministic stratified pseudo-random split with fixed seed ($42$):
  - **Train Set (70%):** 630 images (105 per class)
  - **Validation Set (15%):** 132 images (22 per class)
  - **Test Set (15%):** 138 images (23 per class)
- **Hash Overlap Verification:**
  - $\text{Train} \cap \text{Val} = 0$
  - $\text{Train} \cap \text{Test} = 0$
  - $\text{Val} \cap \text{Test} = 0$
- **Findings:** Zero exact file duplicates exist across the three partitions. The held-out test set is uncorrupted by train samples.

---

## 4. Deep Dive: AITEX Loom-Batch Leakage Analysis

### 4.1 What Is Loom-Batch Leakage?
In industrial textile manufacturing, fabrics are produced on specific mechanical looms in continuous rolls (or batches). In the AITEX dataset, the filename format encodes this physical acquisition structure:

$$\underbrace{\text{0001}}_{\text{Image ID}}\_\underbrace{\text{002}}_{\text{Loom Roll ID}}\_\underbrace{\text{00}}_{\text{Defect Code}}\text{.png}$$

Each physical loom roll (`002`, `006`, `010`, `016`, `019`, `022`, `023`, `025`, `027`, `029`, `030`, `036`) possesses a distinctive weave pattern, yarn count, lighting response, and camera background signature.

### 4.2 Empirical Leakage Investigation
When the dataset was split in Phase 3 using class-stratified random shuffling (`prepare_aitex_spatial_dataset.py`):

```python
for lbl, group in sorted(by_class.items()):
    rng.shuffle(group)
    # Split into train (70%), val (15%), test (15%)
```

We examined the set of physical loom rolls present in `aitex_train.json` versus `aitex_test.json`:
- **Unique Loom Rolls in Training Set:** `['002', '006', '010', '016', '019', '022', '023', '025', '027', '029', '030', '036']` (12 rolls)
- **Unique Loom Rolls in Test Set:** `['002', '006', '019', '023', '025', '030']` (6 rolls)
- **Intersection ($\text{Train Rolls} \cap \text{Test Rolls}$):** `['002', '006', '019', '023', '025', '030']` (All 6 test rolls appear in training!)

### 4.3 Scientific Consequence
Because every single physical fabric roll in the test set was also present in the training set:
1. **Background Memorization:** The neural network was able to memorize the background weave texture and loom signature of the test images during training.
2. **Inflated Validation Accuracy:** The reported **97.65%** validation accuracy is an artifact of same-loom background correlation rather than true generalization to unseen textile weaves.
3. **Generalization Drop on Novel Weaves:** When evaluated on genuinely unseen physical fabrics, performance drops significantly because the model has not learned invariant defect features independent of weave texture.

---

## 5. Audit Conclusions & Recommendations

1. **Acknowledge Internal Split Limitation:** Historical reports claiming "97.65% defect detection accuracy" must be explicitly contextualized as *intra-loom random patch validation accuracy*, not independent out-of-distribution test accuracy.
2. **Maintain Group-Based Splitting Benchmark:** Future model iterations must employ group-based splits (e.g. `GroupKFold` on loom roll ID) to guarantee that no images from the same fabric roll appear in both training and evaluation splits.
3. **Preserve Raw Dataset Integrity:** The raw data files in `data/` must be maintained in their pristine state without silent re-labeling or modification.
