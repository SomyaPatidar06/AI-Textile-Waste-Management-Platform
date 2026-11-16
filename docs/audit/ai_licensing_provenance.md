# AI Licensing, Intellectual Property, and Dataset Provenance Audit

**Project:** AI Textile Waste Management Platform  
**Document ID:** `AUDIT-PHASE-1.6-DELIV-04`  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Audit Phase:** Phase 1.6 — Integration Readiness and Evidence Verification  
**Status:** COMPLETE / AUDIT-ONLY  

---

## 1. Executive Summary

A core requirement before incorporating any reference code, model weights, or datasets into our public GitHub repository (`https://github.com/SomyaPatidar06/AI-Textile-Waste-Management-Platform`) is a strict audit of intellectual property rights, open-source licensing terms, pretrained backbone grants, and training dataset provenance.

### Key Audit Findings:
1. **Source Code Licenses:** While R9 (Abinash) and R13 (Thanmayee) are licensed under standard permissive MIT terms, **R4 (SorTexAI) contains no root LICENSE file**, meaning all rights are reserved by default under copyright law.
2. **Backbone Model Licenses:** ResNet-18 (BSD-3-Clause / Apache 2.0) and MobileNetV2 (Apache 2.0) permit redistribution and commercial reuse of derivative weights.
3. **Severe Dataset Provenance & Commercial Restrictions:**
   - **R4** explicitly trains on datasets with **strict non-commercial academic research clauses** (`DeepFashion` by CUHK, and `KTH-TIPS2-b` by KTH). Derivative model weights may be encumbered by non-commercial terms.
   - **R9** contains 900 images in `dataset/`, but provides zero origin, attribution, or licensing documentation.
   - **R13** omits its 3,067 training images completely.
4. **Redistribution Policy:** **Redistributing raw reference datasets in our public GitHub repository is BLOCKED.** Model weights must be treated as research/academic artifacts until clean-room retraining with certified open-access data is completed.

---

## 2. Granular Licensing Breakdown by Component

### 2.1 Repository Source Code Licenses

| Repository | Source Repository Identifier | Declared License | Redistribution Rights | Attribution Requirements |
|:---|:---|:---:|:---:|:---|
| **R9 (Abinash)** | `Textile-Waste-Intelligence-Platform-main (4) repo 13` | **MIT License** | Full (Commercial, Modification, Distribution) | Preserve original copyright notice: `Copyright (c) 2026 Abinash Mohapatra` |
| **R13 (Thanmayee)** | `Textile-Waste-management-platform-main` | **MIT License** | Full (Commercial, Modification, Distribution) | Preserve original copyright notice: `Copyright (c) 2026 Thanmayee Nadimpalli` |
| **R14 (Repo 7)** | `ai-textile-waste-intelligence-platform-main (2) repo 7` | **MIT License** | Full (Commercial, Modification, Distribution) | Standard MIT attribution |
| **R1 (Srilakshmi)**| `primary-srilakshmi` | **MIT License** | Full (Commercial, Modification, Distribution) | Standard MIT attribution |
| **R4 (SorTexAI)** | `AI_Textile_Waste_Intelligence_Platform-main repo 3` | **NO LICENSE** | **RESTRICTED / UNCLEAR** | No license grant provided. Code must be cleanly re-implemented rather than copied directly. |

---

## 3. Pretrained Backbone Licenses

Both candidate architectures use standard convolutional backbones pretrained on ImageNet-1K:

1. **PyTorch ResNet-18 (`torchvision.models.resnet18`):**
   - **Upstream Author:** PyTorch / Meta Platforms, Inc.
   - **License:** BSD 3-Clause License.
   - **Commercial Rights:** Fully permissive for commercial use, private use, and redistribution with copyright retention.
2. **Keras MobileNetV2 (`tensorflow.keras.applications.MobileNetV2`):**
   - **Upstream Author:** Google LLC / TensorFlow Authors.
   - **License:** Apache License, Version 2.0.
   - **Commercial Rights:** Fully permissive with patent grant, modification notices, and attribution.

---

## 4. Training Dataset Provenance and Encumbrances

An open-source MIT license on a repository's source code **does not grant redistribution rights for the underlying training datasets or derivative model weights**. Each dataset utilized by the reference models was traced to its original source:

### 4.1 R4 (SorTexAI) Dataset Dependencies (`ml_engine/data_preprocessing.py`)

```
R4 Pipeline Source Code (data_preprocessing.py)
   ├── prepare_deepfashion()    ──► DeepFashion (CUHK)
   │                                 └── Restriction: Non-Commercial Research Only!
   ├── prepare_tips()           ──► KTH-TIPS2-b (KTH)
   │                                 └── Restriction: Non-Commercial Research Only!
   ├── prepare_fabric_ibug()    ──► iBUG Texture Dataset (Imperial College)
   │                                 └── Restriction: Academic / Research Only!
   ├── prepare_fashion_mnist()  ──► Fashion-MNIST (Zalando Research)
   │                                 └── License: MIT License (Permissive)
   └── prepare_defects()        ──► Unnamed Textile Defect Dataset
```

#### Detailed Dataset Analysis for R4:
1. **DeepFashion (Chinese University of Hong Kong):**
   - *Clause:* The DeepFashion database is available for non-commercial research purposes only. Commercial exploitation is strictly prohibited without explicit written licensing agreements.
   - *Impact on R4 Weights:* The `garment_classifier.pt` model was trained directly on DeepFashion annotations (`list_category_cloth.txt`, line 195). **Redistribution for commercial deployment is BLOCKED.**
2. **KTH-TIPS2-b (KTH Royal Institute of Technology):**
   - *Clause:* Distributed strictly for academic benchmarking of texture recognition algorithms.
   - *Impact on R4 Weights:* `material_classifier.pt` ingested KTH-TIPS2 texture patches (`tips`, lines 95-121). Model weights carry non-commercial research limitations.
3. **iBUG Texture Dataset (Imperial College London):**
   - *Clause:* Distributed for non-commercial computer vision research.

### 4.2 R9 (Abinash) Dataset Dependencies (`backend/train_model.py`)
- **Dataset Contents:** 900 JPEG images across 6 folders (`Abaca`, `Cotton`, `Hessian`, `Linen`, `Silk`, `Wool`), exactly 150 images each.
- **Audit Findings:**
  - The repository contains no `README`, `DATASET.md`, or attribution metadata explaining how these 900 images were obtained.
  - Image metadata (EXIF) shows stripped headers.
  - Filenames follow synthetic naming conventions (`Cotton_0.jpg` to `Cotton_149.jpg`), characteristic of scraped or programmatically renamed sets.
  - **Status:** **BLOCKED for public redistribution.** While the repository code is MIT, distributing third-party images of unknown copyright status in a public GitHub repository presents copyright infringement liability.

### 4.3 R13 (Thanmayee) Dataset Dependencies (`Fabric_Defect_Training.ipynb`)
- **Dataset Contents:** 3,067 images across 9 defect classes.
- **Audit Findings:**
  - The dataset was stored in a private local folder (`C:\Users\thanm\OneDrive\Desktop\...`) and was never committed to Git.
  - Filenames and class taxonomy match the popular Kaggle "Textile Defect Dataset".
  - **Status:** **BLOCKED.** Dataset is unavailable in repository.

---

## 5. Model Weight Redistribution Legal Analysis

Under contemporary copyright law and software licensing jurisprudence:
1. **Model Weights as Numerical Tensors:** Model weight tensors ($\sim 11.2\text{M}$ floating-point numbers) represent learned mathematical parameters. In many jurisdictions, raw mathematical weights are not eligible for traditional copyright unless they encapsulate expressive source code.
2. **Contractual Terms of Service:** Even if weights themselves are non-copyrightable, the terms of service of proprietary datasets (such as DeepFashion) create contractual obligations binding any party that downloaded the data and trained the weights.
3. **Public GitHub Repository Policy:**
   - Git repositories are not optimized for large binary blobs (a single commit of 4 models exceeds 140 MB, triggering GitHub push warnings or LFS quota exhaustion).
   - Committing weights derived from non-commercial academic datasets into an MIT-licensed public repository creates legal ambiguity regarding commercial applicability.

---

## 6. Intellectual Property Action Plan and Status Summary

| Item | Technical Description | Legal / Licensing Status | Action Required |
|:---|:---|:---:|:---|
| **R9 Code Logic** | FastAPI endpoints & ResNet loading | `VERIFIED - MIT` | Freely adapt; include Abinash copyright notice in credits. |
| **R9 Model Weights** | `fabric_model_v2.pth` (42.7 MB) | `PERMISSIBLE FOR DEMO / ACADEMIC` | Host via external release/artifact storage; do not commit directly to git tree. |
| **R9 Dataset Images** | 900 images in `dataset/` | `BLOCKED - PROVENANCE UNKNOWN` | **DO NOT commit to public GitHub repository.** Add to `.gitignore`. |
| **R4 Code Logic** | `serve.py`, `color_analyzer.py` | `RESTRICTED - NO LICENSE` | **Do not copy raw files.** Clean-room reimplement the architectural ideas. |
| **R4 Model Weights** | `material_classifier.pt`, etc. | `PERMISSIBLE FOR DEMO / ACADEMIC` | Host via external storage; mark as non-commercial research derivatives. |
| **R4 Training Data** | DeepFashion, KTH-TIPS2 | `BLOCKED - NON-COMMERCIAL` | Prohibited from commercial redistribution. |
| **R13 Code Logic** | Flask routes & sustainability math | `VERIFIED - MIT` | Freely adapt; include Thanmayee copyright notice in credits. |
| **R13 Model Weights** | `fabric_defect_model.keras` | `DEPRECATED - PERFORMANCE FLAW` | Discard in favor of PyTorch 7-class taxonomy. |

---

## 7. Formal Attribution Table for Upstream Authors

In compliance with open-source licensing standards, the following attribution notices will be incorporated into the target repository's `CREDITS.md` and documentation:

```markdown
### Upstream Attribution and Open-Source Acknowledgments

This project utilizes architectural patterns, research concepts, and reference implementations from the following open-source contributors:

1. **Abinash Mohapatra** (`Textile-Waste-Intelligence-Platform`)
   - *Contribution:* ResNet-18 fine-tuning methodology and natural fiber classification pipeline.
   - *License:* MIT License (Copyright 2026 Abinash Mohapatra).

2. **Thanmayee Nadimpalli** (`Textile-Waste-management-platform`)
   - *Contribution:* Circularity scoring equations, environmental impact calculations, and defect taxonomy references.
   - *License:* MIT License (Copyright 2026 Thanmayee Nadimpalli).

3. **Srilakshmi Kommu** (`textile-waste-intelligence-platform`)
   - *Contribution:* Full-stack enterprise platform architecture, Next.js frontend design, and PostgreSQL schema.
   - *License:* MIT License (Copyright 2026 Srilakshmi Kommu).

4. **SorTexAI Team** (`AI_Textile_Waste_Intelligence_Platform`)
   - *Contribution:* Commercial waste stream taxonomy and multi-task microservice architecture.
```
