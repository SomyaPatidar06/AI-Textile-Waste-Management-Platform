# AI Model Integration Readiness Assessment

**Project:** AI Textile Waste Management Platform  
**Document ID:** `AUDIT-PHASE-1.6-DELIV-01`  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Audit Phase:** Phase 1.6 — Integration Readiness and Evidence Verification  
**Status:** COMPLETE / AUDIT-ONLY  

---

## 1. Executive Summary

This document establishes the technical integration readiness of candidate deep learning models evaluated during Phase 1.5 for the AI Textile Waste Management Platform. Four candidate checkpoints across three reference repositories were inspected at the binary, parameter, and code execution levels:

1. **R9 Material Classifier:** `backend/fabric_model_v2.pth` (Abinash Mohapatra, Repo 13)
2. **R4 Material Classifier:** `ml_engine/models/material_classifier.pt` (SorTexAI, Repo 3)
3. **R4 Defect Classifier:** `ml_engine/models/defect_classifier.pt` (SorTexAI, Repo 3)
4. **R13 Defect Classifier:** `model/fabric_defect_model.keras` & `backend/ai/textile_model.keras` (Thanmayee Nadimpalli)

Each model was analyzed for checkpoint integrity, parameter completeness, tensor dimensions, preprocessing consistency between training and inference, label alignments, runtime dependencies, and host operating system compatibility.

---

## 2. Model 1: R9 Fabric Material Classifier (`fabric_model_v2.pth`)

### 2.1 Artifact Metadata & Location
- **Source Path:** `reference-repositories\Textile-Waste-Intelligence-Platform-main (4) repo 13\Textile-Waste-Intelligence-Platform-main\backend\fabric_model_v2.pth`
- **File Size:** 44,795,739 bytes (~42.72 MB)
- **Framework:** PyTorch (`torch.save` checkpoint dictionary)
- **Base Architecture:** ResNet-18 (`torchvision.models.resnet18`)
- **Total Parameters:** 11,179,590 parameters (all float32)
- **Audit Status:** `VERIFIED`

### 2.2 Checkpoint Structure & Parameter Inspection
The checkpoint is stored as a Python dictionary containing both model parameters and training provenance:
```python
{
    "model_state_dict": OrderedDict(...),          # 122 parameter tensors
    "class_names": ['Abaca', 'Cotton', 'Hessian', 'Linen', 'Silk', 'Wool'],
    "num_classes": 6,
    "best_validation_accuracy": 95.45454545454545,  # 126/132 validation samples
    "test_accuracy": 92.7536231884058,              # 128/138 held-out test samples
    "architecture": "resnet18",
    "image_size": 224,
    "normalization_mean": [0.485, 0.456, 0.406],
    "normalization_std": [0.229, 0.224, 0.225]
}
```
- **Classification Head:** Linear layer `fc.weight` of shape `[6, 512]` and `fc.bias` of shape `[6]`.
- **Integrity Check:** Checkpoint contains all 122 ResNet-18 weight and bias tensors (`conv1`, `bn1`, `layer1` through `layer4`, and `fc`). No missing or uninitialized parameters.

### 2.3 Preprocessing & Tensor Pipeline
- **Input Dimensions:** `(Batch_Size, 3, 224, 224)`
- **Color Channel Order:** RGB (`PIL.Image.open(...).convert("RGB")`)
- **Normalization:** ImageNet statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$)
- **Preprocessing Discrepancy Found:**
  - *Training Script (`backend/train_model.py`, line 88):* Evaluation transform applied `transforms.Resize(256)` followed by `transforms.CenterCrop(224)`.
  - *Inference Script (`backend/main.py`, line 493):* Inference transform applied direct `transforms.Resize((224, 224))`, which alters the image aspect ratio for non-square inputs.
  - *Recommendation:* Normalize inference preprocessing to `Resize(256)` + `CenterCrop(224)` to match the empirical evaluation transform.

### 2.4 Output Mapping
| Output Index | Class Label | Fiber Category | Target Waste Applications |
|:---:|:---|:---|:---|
| 0 | `Abaca` | Natural Plant (Leaf) | Cordage, specialty paper, industrial textiles |
| 1 | `Cotton` | Natural Plant (Seed) | Mechanical shredding, yarn spinning, insulation |
| 2 | `Hessian` | Natural Plant (Bast/Jute) | Geotextiles, composite reinforcement, sacking |
| 3 | `Linen` | Natural Plant (Bast/Flax) | Premium home textiles, paper pulp, composites |
| 4 | `Silk` | Natural Animal (Protein) | Luxury garments, precision fiber extraction |
| 5 | `Wool` | Natural Animal (Protein) | Shoddy production, acoustic insulation, felting |

### 2.5 Standalone Inference Reproducibility
- **Status:** Fully reproducible without access to the training dataset.
- **Loading Mechanism:**
  ```python
  import torch, torchvision.models as models
  ckpt = torch.load("fabric_model_v2.pth", map_location="cpu", weights_only=False)
  model = models.resnet18(weights=None)
  model.fc = torch.nn.Linear(model.fc.in_features, ckpt["num_classes"])
  model.load_state_dict(ckpt["model_state_dict"])
  model.eval()
  ```

---

## 3. Model 2: R4 Commercial Material Classifier (`material_classifier.pt`)

### 3.1 Artifact Metadata & Location
- **Source Path:** `reference-repositories\AI_Textile_Waste_Intelligence_Platform-main repo 3\AI_Textile_Waste_Intelligence_Platform-main\ml_engine\models\material_classifier.pt`
- **File Size:** 44,805,941 bytes (~42.82 MB)
- **Framework:** PyTorch (`collections.OrderedDict` state dictionary)
- **Base Architecture:** ResNet-18 (`torchvision.models.resnet18`)
- **Total Parameters:** 11,182,155 parameters (all float32)
- **Audit Status:** `VERIFIED` (Weights intact; evaluation claims `UNVERIFIED`)

### 3.2 Checkpoint Structure & Parameter Inspection
- Stored as a raw PyTorch `OrderedDict` representing `model.state_dict()`.
- Metadata is decoupled and stored in companion file `material_labels.json`.
- **Classification Head:** Linear layer `fc.weight` of shape `[11, 512]` and `fc.bias` of shape `[11]`.
- **Integrity Check:** Checkpoint contains all 122 ResNet-18 weight and bias tensors. Fully compatible with `torchvision.models.resnet18(weights=None)`.

### 3.3 Preprocessing & Tensor Pipeline
- **Input Dimensions:** `(Batch_Size, 3, 224, 224)`
- **Color Channel Order:** RGB (`PIL.Image.open(...).convert("RGB")`)
- **Normalization:** ImageNet statistics ($\mu = [0.485, 0.456, 0.406]$, $\sigma = [0.229, 0.224, 0.225]$)
- **Preprocessing Discrepancy Found:**
  - *Training Script (`ml_engine/vision_model.py`, line 28):* `EVAL_TRANSFORM = transforms.Resize((224, 224))`.
  - *Inference Script (`ml_engine/serve.py`, line 62):* Introduces `MATERIAL_TRANSFORM`:
    ```python
    transforms.CenterCrop(int(224 * 0.6)),  # Crop central 134x134 pixels
    transforms.Resize((224, 224)),          # Upscale back to 224x224
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ```
  - *Finding:* The author introduced a 60% center-crop heuristic at inference time to simulate a "macro zoom" into fabric texture. However, the model was trained on uncropped images. This introduces potential domain drift.

### 3.4 Output Mapping
Class labels defined in `ml_engine/models/material_labels.json`:
| Index | Class Label | Fiber Nature | Commercial Waste Stream Category |
|:---:|:---|:---|:---|
| 0 | `Cotton` | Natural Cellulose | Post-consumer clothing, cut waste |
| 1 | `Polyester` | Synthetic Polymer | Fleece, sportswear, PET bottle blends |
| 2 | `Poly-Cotton Blend` | Mixed / Composite | Standard poly-cotton garments (demanding separation) |
| 3 | `Denim` | Heavy Cotton Twill | Blue jeans, workwear |
| 4 | `Wool` | Natural Protein | Knitwear, suiting |
| 5 | `Silk` | Natural Protein | Luxury items |
| 6 | `Linen` | Natural Flax | Summer apparel, beddings |
| 7 | `Viscose` | Regenerated Cellulose | Rayon apparel, linings |
| 8 | `Nylon` | Synthetic Polyamide | Activewear, swimsuits, outerwear |
| 9 | `Leather` | Natural Animal Skin | Footwear, jackets, upholstery |
| 10 | `Mixed/Unknown` | Indeterminate / Blended | Multi-fiber post-consumer waste |

### 3.5 Standalone Inference Reproducibility
- **Status:** Fully reproducible without access to training datasets.

---

## 4. Model 3: R4 Defect Classifier (`defect_classifier.pt`)

### 4.1 Artifact Metadata & Location
- **Source Path:** `reference-repositories\AI_Textile_Waste_Intelligence_Platform-main repo 3\AI_Textile_Waste_Intelligence_Platform-main\ml_engine\models\defect_classifier.pt`
- **File Size:** 44,797,781 bytes (~42.73 MB)
- **Framework:** PyTorch (`collections.OrderedDict` state dictionary)
- **Base Architecture:** ResNet-18
- **Total Parameters:** 11,180,103 parameters (all float32)
- **Audit Status:** `VERIFIED`

### 4.2 Checkpoint Structure & Parameter Inspection
- Stored as raw `OrderedDict`. Companion metadata in `defect_labels.json`.
- **Classification Head:** Linear layer `fc.weight` of shape `[7, 512]` and `fc.bias` of shape `[7]`.
- All 122 ResNet-18 tensors are intact.

### 4.3 Preprocessing & Tensor Pipeline
- **Input Dimensions:** `(Batch_Size, 3, 224, 224)`
- **Color Channel Order:** RGB
- **Transforms (`ml_engine/serve.py`, line 21):** Direct `Resize((224, 224))` with ImageNet normalization. No center crop is applied (unlike material classifier).

### 4.4 Output Mapping
Class labels defined in `ml_engine/models/defect_labels.json`:
| Index | Class Label | Defect Class Nature | Physical Anomaly Type |
|:---:|:---|:---|:---|
| 0 | `Stain` | Contamination | Discoloration, grease, dye bleeding |
| 1 | `Hole` | Structural Loss | Punctures, moth damage, tears |
| 2 | `Broken Stitch` | Seam Failure | Thread breakage, unravelling |
| 3 | `Needle Mark` | Mechanical Puncture | Sewing machine misfeed, puncture lines |
| 4 | `Pinched Fabric` | Handling / Tension | Creasing, fabric pinch between feed rollers |
| 5 | `Weave Defect` | Manufacturing Flaw | Consolidated horizontal, vertical, line flaws |
| 6 | `Defect Free` | Nominal / Intact | Grade-A textile, undamaged |

### 4.5 Standalone Inference Reproducibility
- **Status:** Fully reproducible without dataset access.

---

## 5. Model 4: R13 Fabric Defect Classifier (`fabric_defect_model.keras`)

### 5.1 Artifact Metadata & Location
- **Source Paths:**
  - `reference-repositories\Textile-Waste-management-platform-main\model\fabric_defect_model.keras`
  - `reference-repositories\Textile-Waste-management-platform-main\backend\ai\textile_model.keras`
  - `reference-repositories\Textile-Waste-management-platform-main\best_model.keras`
- **File Size:** 12,187,006 bytes (~11.62 MB)
- **Framework:** Keras 3 / TensorFlow 2.16+ Functional Model (zipped `.keras` format)
- **Base Architecture:** MobileNetV2 (frozen base) + GlobalAveragePooling2D + Dense(128, relu) + Dropout(0.2) + Dense(9, softmax)
- **Total Parameters:** 2,423,753 parameters (Trainable: 165,257; Non-trainable: 2,258,496)
- **Audit Status:** `VERIFIED`

### 5.2 Preprocessing & Tensor Pipeline
- **Input Dimensions:** `(Batch_Size, 224, 224, 3)` (TensorFlow channels-last format)
- **Color Channel Order:** RGB
- **Normalization:** Simple rescaling `1.0 / 255.0` (range `[0.0, 1.0]`).
- **Important:** Does **not** use ImageNet normalization ($\mu/\sigma$). Using ImageNet normalization on this model breaks predictions.

### 5.3 Output Mapping & Companion Artifacts
- **Companion Artifact:** `reference-repositories\Textile-Waste-management-platform-main\backend\ai\label_encoder.pkl` (scikit-learn `LabelEncoder`).
- **9 Raw Classes:**
  `['Broken stitch', 'Needle mark', 'Pinched fabric', 'Vertical', 'defect free', 'hole', 'horizontal', 'lines', 'stain']`

---

## 6. Technical Compatibility Matrix

| Parameter | R9 Material (`.pth`) | R4 Material (`.pt`) | R4 Defect (`.pt`) | R13 Defect (`.keras`) |
|:---|:---|:---|:---|:---|
| **Framework** | PyTorch >= 2.0 | PyTorch >= 2.0 | PyTorch >= 2.0 | TensorFlow >= 2.16 / Keras 3 |
| **Model Size** | 42.72 MB | 42.82 MB | 42.73 MB | 11.62 MB |
| **Parameters** | 11.18 M | 11.18 M | 11.18 M | 2.42 M |
| **Input Shape** | `(B, 3, 224, 224)` | `(B, 3, 224, 224)` | `(B, 3, 224, 224)` | `(B, 224, 224, 3)` |
| **Normalization** | ImageNet ($\mu, \sigma$) | ImageNet ($\mu, \sigma$) | ImageNet ($\mu, \sigma$) | Rescaling (`1/255.0`) |
| **Classes** | 6 | 11 | 7 | 9 |
| **OS Compatibility** | Windows, Linux, macOS | Windows, Linux, macOS | Windows, Linux, macOS | Windows, Linux, macOS |
| **Hardware Reqs** | CPU or CUDA GPU | CPU or CUDA GPU | CPU or CUDA GPU | CPU or CUDA GPU |
| **Inference Time (CPU)** | ~28 ms / image | ~28 ms / image | ~28 ms / image | ~18 ms / image |
| **Self-Contained Weights** | Yes (Dictionary) | Yes (`OrderedDict`) | Yes (`OrderedDict`) | Yes (`.keras` zip) |
| **External Files Req.** | None | `material_labels.json` | `defect_labels.json` | `label_encoder.pkl` |

---

## 7. Integration Risk Assessment & Mitigations

1. **Framework Coexistence Risk:** Running PyTorch (R9, R4) and TensorFlow (R13) in the same Python process introduces heavy memory consumption (>1.2 GB idle RAM) and conflicting C++ runtime library versions (`libomp` / `msvcp140`).
   - *Mitigation:* Convert or standardize models onto a single runtime (e.g., PyTorch ResNet-18 across all tasks, or export all models to ONNX Runtime).
2. **Preprocessing Mismatch Risk:** Applying ImageNet normalization to R13 or applying `1/255.0` to R9/R4 causes severe classification failure.
   - *Mitigation:* Encapsulate preprocessing transformations strictly inside model-specific inference wrappers with unit tests.
3. **Aspect Ratio Distortion:** Direct resizing to `224x224` on high-resolution rectangular phone photos (e.g. 4032x3024) compresses fabric weave geometry by up to 33%.
   - *Mitigation:* Implement letterboxing or standard `Resize(256)` + `CenterCrop(224)`.
