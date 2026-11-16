# Circularity Scoring Engine & Mathematical Validation Report

**Authority Document:** `AI_Textile Waste Intelligence Platform.pdf` (Pages 6–7, Module 9)  
**Target Platform:** AI Textile Waste Management Platform v2.1.0  
**Phase:** Phase 5 — Strict Specification Compliance  
**Date:** November 15, 2026  
**Auditor:** Machine Learning Reliability & Sustainability Analytics Lead  

---

## 1. Executive Summary

This report establishes the mathematical derivation, parameterization, and automated verification of the Waste Scoring Engine defined in Section 4, Module 9 of the specification.

In Phase 5, the circularity evaluation pipeline was upgraded from a heuristic deduction model to the exact five-factor weighted scoring equation prescribed by the specification:
$$\text{Circularity Score} = 0.35 \times \mathcal{S}_{\text{Recyclability}} + 0.20 \times \mathcal{S}_{\text{Condition}} + 0.20 \times \mathcal{S}_{\text{Reuse}} + 0.15 \times \mathcal{S}_{\text{Environmental}} + 0.10 \times \mathcal{S}_{\text{Feasibility}}$$

All sub-scores are normalized on a $[0, 100]$ scale. The output is bounded within $[0, 100]$ and maps to the five recovery potential categories defined on Page 7 of the specification.

---

## 2. Parameterization & Coefficient Taxonomy

### 2.1 Material Baseline Factors (Derived from European Environment Agency / WRAP)

| Material Class | Recyclability ($S_{\text{Recyc}}$) [35%] | Environmental Benefit ($S_{\text{Env}}$) [15%] | Industrial Feasibility ($S_{\text{Feas}}$) [10%] | Base Reuse Potential ($S_{\text{Reuse}}$) [20%] | Primary Recycling Pathway |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **Wool** | 94.0 | 94.0 (24.0 kg CO2 / 4500L H2O) | 90.0 | 92.0 | Fiber Carding / Acoustic Shoddy |
| **Denim** | 92.0 | 92.0 (18.5 kg CO2 / 9500L H2O) | 92.0 | 90.0 | Mechanical Garnetting / Yarn |
| **Cotton** | 90.0 | 90.0 (15.2 kg CO2 / 7800L H2O) | 94.0 | 88.0 | Mechanical Shredding / Spinning |
| **Linen** | 88.0 | 85.0 (12.0 kg CO2 / 2400L H2O) | 88.0 | 85.0 | Mechanical Fiber Recovery |
| **Silk** | 82.0 | 96.0 (28.0 kg CO2 / 3200L H2O) | 75.0 | 95.0 | De-gumming / Luxury Upcycling |
| **Nylon** | 78.0 | 76.0 (11.0 kg CO2 / 750L H2O) | 80.0 | 72.0 | Chemical Hydrolysis (Caprolactam) |
| **Polyester** | 75.0 | 62.0 (8.5 kg CO2 / 550L H2O) | 85.0 | 70.0 | Chemical Depolymerization |
| **Viscose** | 70.0 | 65.0 (9.0 kg CO2 / 1800L H2O) | 70.0 | 68.0 | Solvent Dissolution Recycling |
| **Leather** | 60.0 | 88.0 (32.0 kg CO2 / 12000L H2O) | 55.0 | 82.0 | Bonded Leather Fiber |
| **Poly-Cotton Blend** | 58.0 | 68.0 (10.5 kg CO2 / 3800L H2O) | 50.0 | 55.0 | Hydrothermal Separation |
| **Mixed/Unknown** | 42.0 | 45.0 (6.0 kg CO2 / 1200L H2O) | 35.0 | 40.0 | Thermal Acoustic Battings |

### 2.2 Physical Condition Scoring Factors ($S_{\text{Cond}}$) [20%]

Defect detection models output surface anomaly labels mapped to physical fabric condition scores:

| Surface State / Defect Type | Physical Condition Score ($S_{\text{Cond}}$) | Reuse Degradation Factor | Assessment |
| :--- | :---: | :---: | :--- |
| **Defect Free** | **98.0** | 1.00x | Structurally intact; premium resale/donation candidate. |
| **Needle Mark** | **85.0** | 0.85x | Minor pinhole; non-structural. |
| **Pinched Fabric** | **80.0** | 0.85x | Surface crease; correctable by steaming. |
| **Broken Stitch** | **72.0** | 0.70x | Seam unraveling; mending required. |
| **Weave Defect** | **62.0** | 0.55x | Loom float/mispick; mechanical recycling candidate. |
| **Stain** | **48.0** | 0.35x | Dye or chemical blemish; chemical laundering required. |
| **Hole** | **35.0** | 0.25x | Punctured yarn beam; downcycling candidate. |

---

## 3. Step-by-Step Mathematical Validation

### Case 1: Pristine Natural Cotton (`Cotton`, `Defect Free`)
- $S_{\text{Recyc}} = 90.0$
- $S_{\text{Cond}} = 98.0$
- $S_{\text{Reuse}} = 88.0 \times 1.0 = 88.0$
- $S_{\text{Env}} = 90.0$
- $S_{\text{Feas}} = 94.0$

$$\begin{aligned}
\text{Score} &= 0.35(90.0) + 0.20(98.0) + 0.20(88.0) + 0.15(90.0) + 0.10(94.0) \\
&= 31.50 + 19.60 + 17.60 + 13.50 + 9.40 = \mathbf{91.6}
\end{aligned}$$
- **Assigned Category:** $\ge 85.0 \rightarrow$ **Excellent Recovery Potential**
- **Assigned Waste Stream:** **Reusable**

---

### Case 2: Post-Industrial Denim Scrap with Localized Hole (`Denim`, `Hole`)
- $S_{\text{Recyc}} = 92.0$
- $S_{\text{Cond}} = 35.0$
- $S_{\text{Reuse}} = 90.0 \times 0.25 = 22.5$
- $S_{\text{Env}} = 92.0$
- $S_{\text{Feas}} = 92.0$

$$\begin{aligned}
\text{Score} &= 0.35(92.0) + 0.20(35.0) + 0.20(22.5) + 0.15(92.0) + 0.10(92.0) \\
&= 32.20 + 7.00 + 4.50 + 13.80 + 9.20 = \mathbf{66.7}
\end{aligned}$$
- **Assigned Category:** $50.0 \le 66.7 < 70.0 \rightarrow$ **Moderate Recovery Potential**
- **Assigned Waste Stream:** **Recyclable** (Mechanical Garnetting for Yarn)

---

### Case 3: Poly-Cotton Blend Cutoff with Wrinkle (`Poly-Cotton Blend`, `Pinched Fabric`)
- $S_{\text{Recyc}} = 58.0$
- $S_{\text{Cond}} = 80.0$
- $S_{\text{Reuse}} = 55.0 \times 0.85 = 46.75$
- $S_{\text{Env}} = 68.0$
- $S_{\text{Feas}} = 50.0$

$$\begin{aligned}
\text{Score} &= 0.35(58.0) + 0.20(80.0) + 0.20(46.75) + 0.15(68.0) + 0.10(50.0) \\
&= 20.30 + 16.00 + 9.35 + 10.20 + 5.00 = \mathbf{60.9}
\end{aligned}$$
- **Assigned Category:** $50.0 \le 60.9 < 70.0 \rightarrow$ **Moderate Recovery Potential**
- **Assigned Waste Stream:** **Repairable / Recyclable**

---

### Case 4: Degraded Contaminated Synthetic Waste (`Mixed/Unknown`, `Stain`, `requires_manual=True`)
- $S_{\text{Recyc}} = 42.0$
- $S_{\text{Cond}} = \max(10.0, 48.0 - 10.0) = 38.0$
- $S_{\text{Reuse}} = \max(10.0, 40.0 \times 0.35 - 10.0) = 10.0$
- $S_{\text{Env}} = 45.0$
- $S_{\text{Feas}} = 35.0 \times 0.85 = 29.75$

$$\begin{aligned}
\text{Score} &= 0.35(42.0) + 0.20(38.0) + 0.20(10.0) + 0.15(45.0) + 0.10(29.75) \\
&= 14.70 + 7.60 + 2.00 + 6.75 + 2.98 = \mathbf{34.0}
\end{aligned}$$
- **Assigned Category:** $30.0 \le 34.0 < 50.0 \rightarrow$ **Limited Recovery Potential**
- **Assigned Waste Stream:** **Hazardous Textile Waste / Downcycling**

---

## 4. Verification Evidence

The mathematical accuracy, component breakdown reporting, and category thresholds are validated via automated tests in `tests/test_phase5_specification_compliance.py`:

```python
test_circularity_five_component_mathematical_formula PASSED [100%]
test_circularity_categories_thresholds PASSED              [100%]
```

The scoring engine operates deterministically with zero floating-point accumulation drift and complies fully with Section 4, Module 9 of the specification.
