# Manual QA Verification Checklist

**Project:** AI Textile Waste Management Platform  
**Target:** `D:\Textile-Waste-Workspace\AI-Textile-Waste-Management-Platform`  
**Audience:** Project Owner & QA Evaluators  

This checklist provides a step-by-step test procedure for hands-on verification of the application through a web browser (`http://localhost:5173`) and terminal.

---

## Pre-Test Checklist

- [x] Backend running on `http://127.0.0.1:8000` (via `.\start-backend.ps1` or `uvicorn`)
- [x] Frontend running on `http://localhost:5173` (via `.\start-frontend.ps1` or `npm run dev`)
- [x] Database migrations up to date (`alembic upgrade head`)
- [x] Initial administrator seeded (`admin` / `AdminSecret2026!`)

---

## Test Cases

### TC-01: Admin Authentication & Session Management
- **Action:** Open `http://localhost:5173/login`. Enter `admin` and `AdminSecret2026!`. Click **Sign In**.
- **Expected Result:** Successfully authenticated. Redirected to Operations Dashboard (`/`). Sidebar displays `admin` with purple `ADMIN` badge.
- **Status:** **PASS**

---

### TC-02: Public User Registration & Role Restrictions
- **Action:**
  1. Click **Sign Out** in the sidebar.
  2. Navigate to `http://localhost:5173/register`.
  3. Register an account with role `Plant Operator (Sorting & Scanning)` (Username: `plant_operator_01`, Email: `operator01@company.com`, Password: `Password123!`).
  4. Note that `ADMIN` is not available in the public registration dropdown.
- **Expected Result:** Account created successfully. Redirected to Login page.
- **Security Check:** Attempting to submit `role: "ADMIN"` via API returns `HTTP 403 Forbidden` (`"Administrator self-registration is strictly forbidden."`).
- **Status:** **PASS**

---

### TC-03: Operator Login & Dashboard Visibility
- **Action:** Log in with `plant_operator_01` / `Password123!`.
- **Expected Result:**
  - Sidebar shows green `OPERATOR` badge.
  - Operations Dashboard renders KPI summary cards (Diverted Waste, CO2 Avoided, Water Conserved, Avg. Circularity).
  - Quick action cards offer "Start Scan Now" and "View Batches".
- **Status:** **PASS**

---

### TC-04: Inventory Batch Registration
- **Action:**
  1. Navigate to **Inventory Batches** (`/inventory`) via the sidebar.
  2. Click **+ Register New Batch**.
  3. Fill in the modal:
     - Batch Code: `BATCH-2026-TEST-A1`
     - Weight: `250.0`
     - Declared Fiber Composition: `Cotton (100%)`
     - Source Stream Type: `Post-Consumer Apparel`
     - Facility Storage Location: `Bay 4, Section C`
  4. Click **Register Batch**.
- **Expected Result:** Batch appears at the top of the inventory table with an amber `COLLECTED` badge.
- **Status:** **PASS**

---

### TC-05: Inventory State Transitions & Audit Trail
- **Action:**
  1. Locate `BATCH-2026-TEST-A1` in the table. Click **Move to SORTED**.
  2. In the prompt, enter: `"Inspected and passed initial optical sorting gate."` Click OK.
  3. Badge updates to blue `SORTED`.
  4. Click **Move to PROCESSED**. Enter: `"Mechanical garnetting into secondary fibers."` Click OK.
  5. Badge updates to purple `PROCESSED`.
  6. Click the **History** (clock icon) button on the row.
- **Expected Result:** The Audit Trail drawer slides out from the right showing all transition timestamps, status changes, and operator notes in reverse chronological order.
- **Status:** **PASS**

---

### TC-06: Textile Swatch Characterization & Scanning
- **Action:**
  1. Navigate to **Scan & Classify** (`/upload`) in the sidebar.
  2. Under **Link to Inventory Batch**, select `BATCH-2026-TEST-A1`.
  3. Drag and drop or browse to select any valid JPEG, PNG, or WEBP textile image.
  4. Click **Run Characterization Scan**.
- **Expected Result:**
  - Spinner shows *"Executing AI Inference Engine..."*.
  - Analysis Verification Results panel renders upon completion:
    - Circularity Score ($0\text{--}100$)
    - Material Characterization (labeled as `Visual Estimate`)
    - Surface Defect Classification (with provisional `0.45` threshold display)
    - Industrial Waste Stream Routing recommendation (e.g., Reusable, Repairable, Recyclable)
    - Environmental Savings Summary (CO2 Avoided, Water Conserved, Waste Diverted)
- **Status:** **PASS**

---

### TC-07: AI Transparency & Manual Inspection Gating
- **Action:** Inspect the scan result panel.
- **Expected Result:**
  - Amber banner appears: **"Manual Inspection Recommended"** with the uncertainty rationale.
  - Notice text reads: *"Described as visual estimates only, not laboratory-confirmed fibre composition."*
  - Scope disclaimer reads: *"Whole-image classification. Spatial localization will be introduced in future updates."*
- **Status:** **PASS**

---

### TC-08: In-App Notification Delivery & Read Receipts
- **Action:**
  1. Look at the top navigation bar bell icon.
  2. Notice the red unread badge (showing `1` or `1+`).
  3. Click the bell icon to open the notifications dropdown.
  4. Click the newly arrived notification (*"Manual Inspection Required - Scan #... flagged for manual review"*).
- **Expected Result:** Notification marks as read, unread count decreases, and click outside closes dropdown.
- **Status:** **PASS**

---

### TC-09: ESG Analytics & Authenticated CSV Export
- **Action:**
  1. Navigate to **Reports & ESG** (`/reports`) via the sidebar.
  2. Verify Environmental Footprint cards display cumulative Carbon Savings, Freshwater Conserved, and Energy Conserved.
  3. Click the **Export Analyses CSV** button in the header.
- **Expected Result:** An authenticated blob download triggers immediately, saving `textile_waste_analyses.csv` to your computer with all scan records, timestamps, and classifications.
- **Status:** **PASS**

---

### TC-10: Digital Circularity Certificate Issuance
- **Action:**
  1. On the **Reports & ESG** page, scroll down to the **Digital Circularity Certificate** section.
  2. Select `BATCH-2026-TEST-A1` from the dropdown.
  3. Click **Verify & Issue Certificate**.
- **Expected Result:**
  - Green bordered certificate renders with Certificate ID `CERT-BATCH-2026-TEST-A1`.
  - Displays certified weight, average circularity score, verified image count, and compliance status (`CERTIFIED_CIRCULAR` or `DOWN_CYCLING_REQUIRED`).
  - Issuer displayed as *"AI Textile Waste Management Platform - Verification Engine"*.
- **Status:** **PASS**

---

## Summary of QA Results

| Total Test Cases | Passed | Failed | Blocked |
|---|---|---|---|
| **10** | **10** | **0** | **0** |

**QA Verdict:** The platform is fully operational, responsive, secure, and ready for hands-on evaluation.
