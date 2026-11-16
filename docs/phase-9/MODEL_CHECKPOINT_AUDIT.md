# Phase 9 — Model Checkpoint & Architecture Audit

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Governing Authority:** `AI_Textile Waste Intelligence Platform.pdf`  
**Audit Date:** 2026-11-16  

---

## 1. Executive Summary

An exhaustive audit of all deployed AI model checkpoints, runtime architectures, serialized metadata, and class taxonomies in `backend/app/ai/models/` was performed to resolve historical inconsistencies and establish an authoritative inventory of supported model capabilities.

### Key Resolution of Historical Taxonomy Inconsistency
- **The Conflict:** Historical project reports inconsistently described the material engine. Early Phase 2 documentation cited a 6-class natural fiber classifier (`Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool`). Later Phase 2/3 reports described an 11-class commercial taxonomy (`Cotton`, `Polyester`, `Poly-Cotton Blend`, `Denim`, `Wool`, `Silk`, `Linen`, `Viscose`, `Nylon`, `Leather`, `Mixed/Unknown`).
- **The Empirical Reality:**
  - The actively deployed primary material checkpoint `fabric_model_v2.pth` (and its ONNX equivalent `fabric_model_v2.onnx`) contains a linear classification head with **exactly 6 output units** (`shape: [6, 512]`). Its internal serialized metadata confirms the classes: `['Abaca', 'Cotton', 'Hessian', 'Linen', 'Silk', 'Wool']`.
  - An older legacy checkpoint `material_classifier.pt` exists in the models directory with 11 output units (`shape: [11, 512]`).
  - In `MaterialEngine` (`backend/app/ai/material_engine.py`), `fabric_model_v2.pth` is explicitly prioritized and loaded.
  - **Verdict:** The platform genuinely recognizes **6 natural textile fibers**. Advertising commercial synthetic classifications (such as pure Polyester, Nylon, or Leather) as fully trained primary outputs is factually incorrect. The application correctly handles broader waste categories through rule-based circularity mappings, but optical RGB predictions must strictly reflect the genuine 6-class natural taxonomy.

---

## 2. Checkpoint Inventory & Serialization Audit

| Checkpoint File | Size (MB) | Format | Framework | Backbone Architecture | Linear Head Shape | Genuine Classes Count | Operational Role |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **`fabric_model_v2.pth`** | 42.72 MB | PTH | PyTorch | ResNet-18 | `[6, 512]` | 6 | **Primary Material Classifier** |
| **`fabric_model_v2.onnx`** | 42.64 MB | ONNX | ONNX Runtime | ResNet-18 | `[1, 6]` | 6 | **Accelerated Material Inference** |
| **`material_classifier.pt`** | 42.73 MB | PT | PyTorch | ResNet-18 | `[11, 512]` | 11 | Legacy Prototype (Standby) |
| **`aitex_defect_model.pth`** | 42.72 MB | PTH | PyTorch | ResNet-18 | `[6, 512]` | 6 | **Primary Defect Detector Head** |
| **`aitex_defect_model.onnx`** | 42.64 MB | ONNX | ONNX Runtime | ResNet-18 | `[1, 6]` | 6 | **Accelerated Defect Inference** |
| **`defect_classifier.pt`** | 42.73 MB | PT | PyTorch | ResNet-18 | `[7, 512]` | 7 | Legacy Prototype (Standby) |

---

## 3. Detailed Model Head & Serialization Inspection

### 3.1 Primary Material Classifier (`fabric_model_v2.pth`)
- **File Size:** 44,797,323 bytes (42.72 MB)
- **Top-Level Keys:** `['model_state_dict', 'class_names', 'num_classes', 'best_validation_accuracy', 'test_accuracy', 'architecture', 'image_size', 'normalization_mean', 'normalization_std']`
- **Serialized Class Names:** `['Abaca', 'Cotton', 'Hessian', 'Linen', 'Silk', 'Wool']`
- **Output Linear Layer:** `fc.weight`: `torch.Size([6, 512])`, `fc.bias`: `torch.Size([6])`
- **Reported Metadata Metrics:**
  - `best_validation_accuracy`: 95.45%
  - `test_accuracy`: 92.75%
  - `architecture`: `resnet18`
  - `image_size`: 224
  - `normalization_mean`: `[0.485, 0.456, 0.406]`
  - `normalization_std`: `[0.229, 0.224, 0.225]`

### 3.2 Primary Defect Classifier (`aitex_defect_model.pth`)
- **File Size:** 44,797,259 bytes (42.72 MB)
- **Structure:** Direct `state_dict` with 122 layer keys.
- **Output Linear Layer:** `fc.weight`: `torch.Size([6, 512])`, `fc.bias`: `torch.Size([6])`
- **Label Mapping Source:** `backend/app/ai/models/aitex_defect_labels.json`
- **Verified Classes:**
  1. `Defect Free`
  2. `Weave Defect`
  3. `Hole`
  4. `Stain`
  5. `Pinched Fabric`
  6. `Broken Stitch`
- **Training Provenance:** Fine-tuned on the AITEX fabric defect database for 8 epochs (`aitex_defect_training_history.json`).

### 3.3 Accelerated ONNX Checkpoints (`fabric_model_v2.onnx`, `aitex_defect_model.onnx`)
- **IR Version:** 10 / Opset 17
- **Input Node:** Name: `input`, Dimensions: `['batch_size', 3, 224, 224]`, Type: `tensor(float)`
- **Output Node:** Name: `output`, Dimensions: `['batch_size', 6]`, Type: `tensor(float)`
- **Verification:** Both ONNX models have been verified for exact shape compatibility and numerical equivalence with their respective PyTorch checkpoints.

---

## 4. Deployed Class Taxonomy Matrix

| Model | Checkpoint File | Active Label File | Confirmed Classes |
| :--- | :--- | :--- | :--- |
| **Material** | `fabric_model_v2.pth` / `.onnx` | Embedded metadata | `Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool` (6 classes) |
| **Defect** | `aitex_defect_model.pth` / `.onnx` | `aitex_defect_labels.json` | `Defect Free`, `Weave Defect`, `Hole`, `Stain`, `Pinched Fabric`, `Broken Stitch` (6 classes) |

---

## 5. Architectural Recommendations for Public Release

1. **Explicit Documentation:** The public `README.md` and API specifications must clearly document that the deep learning material engine is trained on **6 natural textile fibers**. Broader fiber blends and synthetics are handled through the circularity and inventory rules engines, but optical classification models must not make unsupported claims regarding synthetic fiber dissolution.
2. **Option B Policy Enforcement:** Because optical classification is restricted to visual surface features, all material predictions must continue to carry the mandatory `(Visual Estimate)` qualification.
3. **Weight Exclusion from Git:** Binary weights totaling over 250 MB (`*.pth`, `*.pt`, `*.onnx`) are correctly excluded by `.gitignore`. A download script or release asset link should be provided for public evaluation.
