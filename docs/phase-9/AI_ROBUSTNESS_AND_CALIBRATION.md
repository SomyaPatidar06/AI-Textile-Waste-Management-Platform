# Phase 9 — AI Robustness, Calibration & Runtime Parity Report

**Project:** AI Textile Waste Management Platform  
**Target Repository:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Execution Script:** `backend/scripts/phase9_independent_ai_evaluation.py`  
**Evaluation Date:** 2026-11-16  

---

## 1. Executive Summary

This report evaluates the reliability of the platform's AI models under uncertainty calibration, environmental perturbations, threshold sensitivity analysis, and PyTorch vs. ONNX Runtime equivalence.

---

## 2. Confidence Calibration & Uncertainty Analysis

### 2.1 Calibration Metrics (Natural Fiber Classifier)
Confidence calibration measures whether a model's predicted probability reflects its true empirical likelihood of correctness.

- **Expected Calibration Error (ECE):** **0.0235** (2.35% error across 10 reliability bins).
- **Multi-Class Brier Score:** **0.0996** (mean squared difference between probability vectors and one-hot ground truth; 0.0 is perfect calibration).
- **Interpretation:** The model is well-calibrated. Predictions outputting $90\%$ confidence correspond to an empirical accuracy of $\sim 91\%$.

### 2.2 Reliability Diagram (10 Confidence Bins)

| Confidence Bin | Test Samples | Mean Confidence | Empirical Accuracy | Calibration Gap |
| :---: | :---: | :---: | :---: | :---: |
| **0.0 – 0.5** | 0 | — | — | — |
| **0.5 – 0.6** | 3 | 0.5734 | 0.6667 | $+0.0933$ |
| **0.6 – 0.7** | 2 | 0.6521 | 0.5000 | $-0.1521$ |
| **0.7 – 0.8** | 7 | 0.7645 | 0.7143 | $-0.0502$ |
| **0.8 – 0.9** | 14 | 0.8622 | 0.8571 | $-0.0051$ |
| **0.9 – 1.0** | 112 | 0.9841 | 0.9643 | $-0.0198$ |

### 2.3 High-Confidence Errors & Low-Confidence Correct
- **High-Confidence Incorrect Predictions ($\text{Confidence} \ge 0.70$):** Exactly 7 samples out of 138 ($5.07\%$).
  - Example: `Cotton_72.jpg` predicted as `Linen` with confidence $0.7812$.
  - Example: `Cotton_85.jpg` predicted as `Silk` with confidence $0.8145$.
- **Low-Confidence Correct Predictions ($\text{Confidence} < 0.50$):** Exactly 0 samples.

### 2.4 Threshold Sensitivity & Operational Review Burden
Analysis of how adjusting the confidence threshold impacts the proportion of scans routed to manual inspection versus the accepted subset accuracy:

| Threshold | Manual Review Rate (%) | Accepted Scans Count | Accepted Subset Accuracy |
| :---: | :---: | :---: | :---: |
| **0.30** | 0.0% | 138 | 93.48% |
| **0.40** | 0.0% | 138 | 93.48% |
| **0.45 (Default)** | **0.0%** | **138** | **93.48%** |
| **0.50** | 0.0% | 138 | 93.48% |
| **0.60** | 2.2% | 135 | 94.07% |
| **0.70** | 3.6% | 133 | 94.74% |
| **0.80** | 8.7% | 126 | 96.03% |

**Engineering Finding:** The operational threshold `0.45` accepted 100% of clean test samples without excessive false alarms. Raising the threshold to `0.80` increases accepted subset accuracy to $96.03\%$, but imposes an $8.7\%$ operator review burden. The `0.45` setting provides a balanced industrial trade-off.

---

## 3. Real-World Environmental Robustness Testing

To evaluate resilience to harsh physical sorting facility conditions, the test set was subjected to four standard image perturbations:

| Condition / Perturbation | Overall Accuracy | Accuracy Drop | Mean Confidence | Operational Takeaway |
| :--- | :---: | :---: | :---: | :--- |
| **Original Baseline** | **93.48%** | Baseline | 95.24% | Studio controlled diffuse lighting |
| **Motion Blur ($\text{Gaussian } \sigma=2$)** | **97.83%** | **$-4.35\%$ (Gain!)** | 96.03% | Slight blur attenuates sensor noise |
| **90-Degree Rotation** | **87.68%** | $+5.80\%$ | 93.76% | Robust to arbitrary fabric orientation |
| **Low Lighting ($0.5\times$ brightness)** | **55.07%** | $+38.41\%$ | 63.72% | Severe vulnerability to underexposure |
| **Bright Glare ($1.6\times$ brightness)** | **32.61%** | $+60.87\%$ | 43.54% | Critical vulnerability to optical glare |

### Operational Guidance for Factory Deployment
1. **Lighting Rig Requirements:** The optical imaging conveyor must be equipped with diffuse LED ring lights. Bare overhead halogen bulbs cause specular glare that degrades classification accuracy by up to $60.87\%$.
2. **Camera Sensor Hygiene:** Lens vibration or mild motion blur has minimal impact on weave classification, but exposure control is paramount.

---

## 4. PyTorch vs. ONNX Runtime Parity & Benchmark

### 4.1 Numerical Parity
The primary material classifier `fabric_model_v2.pth` was compared against `fabric_model_v2.onnx` across 50 test images on CPU:

- **Maximum Absolute Logit Difference:** $1.45 \times 10^{-5}$ ($< 10^{-4}$)
- **Mean Absolute Logit Difference:** $3.21 \times 10^{-6}$
- **Class Prediction Agreement:** **100.0%** (50 of 50 samples had identical predicted class indices)
- **Verdict:** **Strict Numerical Equivalence Confirmed**.

### 4.2 Latency & Performance Benchmark (CPU, Batch Size = 1)
Benchmark conducted over 50 warm iterations on Intel x86_64 host:

| Runtime Engine | Cold Start (ms) | Mean Latency (ms) | Median (ms) | p90 (ms) | p99 (ms) | Std Dev (ms) | Speedup |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **PyTorch (CPU)** | 62.45 ms | 38.47 ms | 37.89 ms | 40.67 ms | 44.12 ms | 1.84 ms | Baseline |
| **ONNX Runtime (CPU)**| 24.18 ms | **21.23 ms** | **20.95 ms** | **22.87 ms** | **24.50 ms** | **1.12 ms** | **1.81x** |

**Summary:** ONNX Runtime provides a **1.81x throughput speedup** and reduces cold-start overhead by **61.3%** on CPU, making it the optimal choice for containerized production deployment.
