# ONNX Optimization & Numerical Verification Report

**Target Platform:** AI Textile Waste Management Platform v2.1.0  
**Phase:** 4.2 — Model Optimization  
**Date:** November 15, 2026  
**Artifacts Generated:**  
- `backend/app/ai/models/fabric_model_v2.onnx` (42.64 MB)
- `backend/app/ai/models/aitex_defect_model.onnx` (42.64 MB)
- `docs/phase-4/onnx_optimization_data.json`  

---

## 1. Executive Summary

To achieve production-grade inference latencies on standard CPU deployments without sacrificing prediction fidelity, both ResNet-18 classifiers were compiled to the Open Neural Network Exchange (ONNX) format using Opset 17 with dynamic batch axes.

Comprehensive validation confirmed:
- **Numerical Parity:** 100.0% top-1 prediction agreement across all test inputs with max absolute output divergence $< 2.1 \times 10^{-5}$ and cosine similarity equal to $1.000000$.
- **Latency Improvements:** 2.80x speedup on single swatches (15.4 ms vs 43.2 ms) and 2.08x speedup on 31-patch full roll scans (501.6 ms vs 1043.7 ms).
- **Zero-Downtime Reliability:** Both inference engines (`MaterialEngine` and `SpatialDefectDetector`) implement automated runtime discovery and transparent fallback to PyTorch if ONNX models or runtimes are unavailable.

---

## 2. Export Architecture & Toolchain

### 2.1 Exporter Configuration
In PyTorch 2.15 on Python 3.14, the standard `torch.onnx.export()` function defaults to the TorchDynamo exporter which requires external third-party packages (`onnxscript`). To ensure robust, self-contained compilation using native C++ kernels, `dynamo=False` was explicitly set.

```python
torch.onnx.export(
    model,
    dummy_input,
    onnx_file_path,
    export_params=True,
    opset_version=17,
    do_constant_folding=True,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={
        "input": {0: "batch_size"},
        "output": {0: "batch_size"}
    },
    dynamo=False
)
```

### 2.2 Model Specifications

| Parameter | Material Classifier (`fabric_model_v2`) | Defect Classifier (`aitex_defect_model`) |
| :--- | :--- | :--- |
| **Base Architecture** | ResNet-18 (Torchvision compatible) | ResNet-18 (Torchvision compatible) |
| **Input Tensor Shape** | `(B, 3, 224, 224)` float32 | `(B, 3, 224, 224)` float32 |
| **Normalization** | ImageNet Mean & Std ($\mu=[0.485, 0.456, 0.406]$, $\sigma=[0.229, 0.224, 0.225]$) | ImageNet Mean & Std ($\mu=[0.485, 0.456, 0.406]$, $\sigma=[0.229, 0.224, 0.225]$) |
| **Output Shape** | `(B, 6)` unnormalized logits | `(B, 6)` unnormalized logits |
| **ONNX File Size** | **42.64 MB** | **42.64 MB** |
| **Original `.pth` Size** | 44.70 MB | 44.70 MB |
| **Size Reduction** | 4.6% reduction (removal of optimizer metadata) | 4.6% reduction (removal of optimizer metadata) |

---

## 3. Numerical Equivalence Verification

To prove that the ONNX graph computes identical results to the native PyTorch checkpoint, 50 real textile test samples were fed through both engines simultaneously. Logits were captured and compared across four mathematical criteria:
1. **Top-1 Concordance:** The percentage of samples where $\text{argmax}(\mathbf{z}_{\text{PyTorch}}) = \text{argmax}(\mathbf{z}_{\text{ONNX}})$.
2. **Maximum Absolute Difference:** $\max |\mathbf{z}_{\text{PyTorch}} - \mathbf{z}_{\text{ONNX}}|$.
3. **Mean Absolute Difference:** $\frac{1}{N \cdot C} \sum |\mathbf{z}_{\text{PyTorch}} - \mathbf{z}_{\text{ONNX}}|$.
4. **Cosine Similarity:** $\frac{\mathbf{z}_{\text{PyTorch}} \cdot \mathbf{z}_{\text{ONNX}}}{\|\mathbf{z}_{\text{PyTorch}}\| \|\mathbf{z}_{\text{ONNX}}\|}$.

### 3.1 Numerical Verification Results

| Metric | Natural Fiber Classifier | AITEX Defect Classifier | Tolerance Threshold | Pass / Fail |
| :--- | :---: | :---: | :---: | :---: |
| **Samples Evaluated** | 50 | 50 | $\ge 50$ | PASS |
| **Top-1 Concordance** | **100.00% (50/50)** | **100.00% (50/50)** | $100.0\%$ | **PASS** |
| **Max Absolute Diff** | $1.955 \times 10^{-5}$ | $2.027 \times 10^{-5}$ | $< 1.0 \times 10^{-4}$ | **PASS** |
| **Mean Absolute Diff** | $2.620 \times 10^{-6}$ | $2.740 \times 10^{-6}$ | $< 1.0 \times 10^{-5}$ | **PASS** |
| **Cosine Similarity** | **1.000000** | **1.000000** | $\ge 0.999999$ | **PASS** |

*Analysis:* Floating-point deviations on the order of $10^{-5}$ are the standard consequence of minor instruction-level differences between PyTorch's ATen backend and ONNX Runtime's fused GEMM/Conv kernels in IEEE 754 single precision. Zero rank order reversals occurred across any sample.

---

## 4. Production Integration & Fallback Strategy

Both `MaterialEngine` (`backend/app/ai/material_engine.py`) and `SpatialDefectDetector` (`backend/app/ai/spatial_detector.py`) were re-engineered with dual-engine architecture:

```
                      [ Client Scan Request ]
                                 |
                                 v
                     [ Engine Initialization ]
                                 |
             +-------------------+-------------------+
             |                                       |
    [ ONNX Model Exists &                   [ ONNX Missing or ]
      onnxruntime Available ]               [ Provider Error  ]
             |                                       |
             v                                       v
    +-------------------+                   +-------------------+
    |    ONNX Runtime   |                   |  PyTorch Fallback |
    | Inference Session |                   |  nn.Module.eval() |
    +-------------------+                   +-------------------+
             |                                       |
             +-------------------+-------------------+
                                 |
                                 v
                     [ Softmax Probabilities ]
```

### Key Implementation Mechanics
1. **Model Discovery:** During `_load_model()`, the engine searches for `*.onnx` first. If present and `onnxruntime` is installed, it instantiates an `InferenceSession` with `SessionOptions(graph_optimization_level=ORT_ENABLE_ALL, intra_op_num_threads=4)`.
2. **Transparent Fallback:** If `onnxruntime` raises an exception during session creation or inference, an `exception` log is written and the engine falls back to standard PyTorch `torch.load()`.
3. **Seamless API:** The prediction methods (`predict_bytes()`, `scan_fabric_roll()`) return identical Python dictionaries containing classification labels, probabilities, bounding boxes, and Option B governance fields regardless of which underlying engine executed the tensor mathematics.
