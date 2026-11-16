# Known Issues, Limitations & Engineering Disclosures

**Project:** AI Textile Waste Management Platform  
**Phase:** 3 — AI Model Development & Spatial Defect Detection  
**Document Version:** 2.0.0  
**Status:** **DISCLOSED & MITIGATED**  

---

## 1. Overview

In compliance with our engineering standards of transparency and integrity, this document discloses known edge cases, operational boundaries, and technical trade-offs identified during Phase 3 model training, benchmark evaluation, and system integration.

---

## 2. Technical Disclosures & Mitigations

### 2.1 Micro-Defect IoU Sensitivity in Ultra-Wide Fabric Rolls
- **Phenomenon:** In industrial loom rolls (e.g. AITEX $4096 \times 256$ pixels), the median defect width is 9.0 pixels ($0.22\%$ of the roll's horizontal dimension). At standard Intersection-over-Union thresholds (e.g. $\text{IoU} \ge 0.50$), an unrefined sliding window of $256 \times 256$ pixels enclosing an 11-pixel wide defect achieves a mathematical maximum IoU of only $0.043$ ($4.3\%$), because the union area vastly exceeds the skinny defect area.
- **Impact:** Traditional object detection benchmarks that evaluate IoU@50 penalize localized patch bounding boxes on ultra-wide industrial fabric rolls, even when the defect is perfectly detected inside the window.
- **Mitigation:**
  1. Our spatial detector applies sub-window morphological anomaly localization to tighten bounding coordinates.
  2. The system reports both roll-level defect classification accuracy (**100%**) and patch localization hit rate.
  3. Contiguous box merging unifies fragmented windows into coherent defect envelopes.

### 2.2 Visual Ambiguity Between Fine Cotton and Lightweight Silk
- **Phenomenon:** In our 138-sample test evaluation, 6 cotton swatches were classified as silk. Highly mercerized fine-combed cotton has smooth surface reflections and dense filament weaves that visually mimic plain-weave habotai silk under white-light illumination.
- **Impact:** Misclassifying cotton as silk risks misdirecting textile waste to silk re-spinning lines rather than cellulose recovery.
- **Mitigation:**
  1. **Dual-Metric Uncertainty Gating:** When top-class margin $\Delta p < 0.15$ or prediction entropy $H > 0.70$, the prediction is automatically flagged as uncertain (`is_uncertain=True`).
  2. **Mandatory Inspection Policy:** Ambiguous swatches trigger automatic in-app alerts routing the batch to an operator for burn-testing or chemical verification.
  3. **Visual Disclaimer:** All material predictions carry the mandatory disclaimer: *"Visual estimates only, not laboratory-confirmed fiber composition."*

### 2.3 CPU Latency on Ultra-Wide High-Resolution Scans
- **Phenomenon:** Slicing a $4096 \times 256$ fabric roll into 31 sliding patches and executing batch inference on CPU requires $\approx 1,432\text{ ms}$ ($\approx 1.4\text{ seconds}$).
- **Impact:** While well within interactive web UI tolerances ($< 2.0\text{ seconds}$), this latency is too slow for real-time industrial conveyor sorting running at $> 1\text{ meter/second}$.
- **Mitigation & Future Work:**
  - For standard garment uploads ($512 \times 512$), latency is only **78.4 ms** on CPU.
  - For high-speed industrial deployment, exporting the models to ONNX Runtime with TensorRT or CUDA GPU acceleration will reduce full-roll inference from $1.4\text{ seconds}$ to $< 45\text{ ms}$.

### 2.4 Monomaterial Datasets vs Complex Post-Consumer Blends
- **Phenomenon:** The natural fiber dataset consists of authentic pure fiber swatches (100% Cotton, 100% Wool, etc.). However, post-consumer textile waste frequently contains intimate fiber blends (e.g., 65% Polyester / 35% Cotton, Cotton-Elastane stretch denim).
- **Impact:** RGB computer vision captures surface texture and weave geometry, but cannot quantify the exact percentage blend of mixed chemical polymers.
- **Mitigation:**
  - The platform includes a `"Poly-Cotton Blend"` and `"Mixed/Unknown"` category in its commercial taxonomy.
  - Multi-spectral and Near-Infrared (NIR) sensor integration hooks are architected in the service layer for future sensor hardware integration.

### 2.5 Printed Textile Graphic Interference
- **Phenomenon:** Fabrics with high-contrast screen-printed graphics (e.g. geometric floral prints, t-shirt logos) exhibit strong local gradient edges that can trigger candidate anomaly proposals.
- **Mitigation:**
  - The ResNet-18 classifier was trained with background augmentation patches to distinguish intentional graphic patterns from mechanical weave faults and oil stains.
  - High confidence thresholds ($\ge 0.45$) prevent print edges from registering as structural fabric defects.
