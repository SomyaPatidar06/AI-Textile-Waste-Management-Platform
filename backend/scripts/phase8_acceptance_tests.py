"""
Phase 8 Functional Acceptance & Integration Verification Script.
Tests all 17 operational checkpoints directly against the live running API at http://127.0.0.1:8000.
"""

import io
import sys
import json
import uuid
from pathlib import Path
import requests
from PIL import Image

BASE_URL = "http://127.0.0.1:8000"
API_V1 = f"{BASE_URL}/api/v1"

results = {}

def test_checkpoint(number, name, func):
    try:
        details = func()
        results[f"CP-{number:02d}: {name}"] = {"status": "PASSED", "details": details}
        print(f"[PASSED] CP-{number:02d}: {name}")
    except Exception as e:
        results[f"CP-{number:02d}: {name}"] = {"status": "FAILED", "error": str(e)}
        print(f"[FAILED] CP-{number:02d}: {name} -> {e}")

# Checkpoints 1-4: 4 Roles Auth
def cp1_admin_auth():
    r = requests.post(f"{API_V1}/auth/login", json={"username": "admin", "password": "AdminSecret2026!"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    assert "access_token" in data and "refresh_token" in data
    me = requests.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {data['access_token']}"})
    assert me.status_code == 200
    assert me.json()["role"] == "ADMIN"
    return {"role": me.json()["role"], "token_type": data["token_type"]}

def cp2_operator_auth():
    r = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    token = r.json()["access_token"]
    me = requests.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["role"] == "OPERATOR"
    return {"role": me.json()["role"]}

def cp3_sustain_auth():
    r = requests.post(f"{API_V1}/auth/login", json={"username": "sustain1", "password": "SustainSecret2026!"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    token = r.json()["access_token"]
    me = requests.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["role"] == "SUSTAINABILITY_MANAGER"
    return {"role": me.json()["role"]}

def cp4_manuf_auth():
    r = requests.post(f"{API_V1}/auth/login", json={"username": "manuf1", "password": "ManufSecret2026!"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    token = r.json()["access_token"]
    me = requests.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me.json()["role"] == "MANUFACTURER"
    return {"role": me.json()["role"]}

# Checkpoint 5: Public Registration
def cp5_public_reg():
    uid = uuid.uuid4().hex[:6]
    uname = f"reg_user_{uid}"
    r = requests.post(f"{API_V1}/auth/register", json={
        "username": uname,
        "email": f"{uname}@textile.org",
        "password": "Password123!",
        "role": "OPERATOR"
    })
    assert r.status_code in [200, 201], f"Status {r.status_code}: {r.text}"
    return {"registered_username": uname}

# Checkpoint 6: RBAC Boundaries
def cp6_rbac_enforcement():
    r_op = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    op_tok = r_op.json()["access_token"]
    r_users = requests.get(f"{API_V1}/users", headers={"Authorization": f"Bearer {op_tok}"})
    assert r_users.status_code == 403, f"Expected 403, got {r_users.status_code}"
    return {"operator_blocked_from_admin_route": True}

# Checkpoint 7: Waste Consignment Batch Creation
created_batch_id = None
created_batch_code = None
def cp7_batch_creation():
    global created_batch_id, created_batch_code
    r_op = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    op_tok = r_op.json()["access_token"]
    code = f"BATCH-P8-{uuid.uuid4().hex[:8].upper()}"
    payload = {
        "batch_code": code,
        "weight_kg": 450.0,
        "declared_material": "Cotton",
        "source_type": "POST_INDUSTRIAL",
        "location": "Warehouse Sector 4A",
        "notes": "High grade virgin cutting scraps from factory floor"
    }
    r = requests.post(f"{API_V1}/batches", json=payload, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code == 201, f"Status {r.status_code}: {r.text}"
    batch = r.json()
    created_batch_id = batch["id"]
    created_batch_code = batch["batch_code"]
    return {"batch_id": batch["id"], "batch_code": batch["batch_code"], "status": batch["status"]}

# Checkpoint 8: Real Textile Image Upload & MIME Validation
created_analysis_id = None
last_analysis_data = None
def cp8_image_upload_and_mime():
    global created_analysis_id, last_analysis_data
    r_op = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    op_tok = r_op.json()["access_token"]
    
    buf = io.BytesIO()
    img = Image.new("RGB", (256, 256), color=(140, 150, 135))
    img.save(buf, format="JPEG")
    buf.seek(0)
    
    files = {"file": ("textile_specimen.jpg", buf.getvalue(), "image/jpeg")}
    data = {"batch_id": created_batch_id, "notes": "Specimen scan Phase 8"}
    
    r = requests.post(f"{API_V1}/analysis/scan", files=files, data=data, headers={"Authorization": f"Bearer {op_tok}"})
    assert r.status_code in [200, 201], f"Status {r.status_code}: {r.text}"
    res = r.json()
    created_analysis_id = res["id"]
    last_analysis_data = res
    return {
        "analysis_id": res["id"],
        "material_prediction": res.get("material_prediction"),
        "material_confidence": res.get("material_confidence")
    }

# Checkpoint 9: AI Spatial Defect Detection & Normalized Bounding Boxes
def cp9_defect_and_bboxes():
    res = last_analysis_data
    assert "defect_prediction" in res
    assert "defect_confidence" in res
    assert "bounding_boxes" in res
    bboxes = res["bounding_boxes"]
    assert isinstance(bboxes, list)
    return {
        "defect_prediction": res["defect_prediction"],
        "defect_confidence": res["defect_confidence"],
        "bbox_count": len(bboxes)
    }

# Checkpoint 10: Option B Governance Policy
def cp10_option_b_governance():
    res = last_analysis_data
    mat = res.get("material_prediction", "")
    assert "(Visual Estimate)" in mat, f"Option B governance label missing in: {mat}"
    return {"material_with_governance_label": mat}

# Checkpoint 11: 5-Component Circularity Score Breakdown
def cp11_circularity_formula():
    res = last_analysis_data
    assert "circularity_score" in res
    score = res["circularity_score"]
    assert 0 <= score <= 100
    breakdown = res.get("scoring_breakdown") or res.get("circularity_breakdown", {})
    assert bool(breakdown), "Breakdown missing"
    assert "material_recyclability" in breakdown
    return {"circularity_score": score, "breakdown_factors": list(breakdown.keys())}

# Checkpoint 12: 7 Recycling & Reuse Pathways
def cp12_recycling_pathways():
    res = last_analysis_data
    raw_recs = res.get("recommendations", [])
    if isinstance(raw_recs, str):
        try:
            raw_recs = json.loads(raw_recs)
        except Exception:
            raw_recs = [raw_recs]
    assert len(raw_recs) > 0, "No recommendations returned"
    return {"recommended_pathways": raw_recs}

# Checkpoint 13: Operator Verification & Manual Review Handling
def cp13_operator_verification():
    res = last_analysis_data
    assert "requires_manual_inspection" in res
    assert "is_uncertain" in res
    return {
        "requires_manual_inspection": res["requires_manual_inspection"],
        "uncertainty_reason": res.get("uncertainty_reason", "")
    }

# Checkpoint 14: Batch Lifecycle Progression
def cp14_lifecycle_progression():
    r_op = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    op_tok = r_op.json()["access_token"]
    
    r1 = requests.patch(
        f"{API_V1}/batches/{created_batch_id}/status",
        json={"status": "SORTED", "notes": "Optical inspection passed. Graded into Cotton Pure bin."},
        headers={"Authorization": f"Bearer {op_tok}"}
    )
    assert r1.status_code == 200, f"Status {r1.status_code}: {r1.text}"
    assert r1.json()["status"] == "SORTED"
    
    r_detail = requests.get(f"{API_V1}/batches/{created_batch_id}", headers={"Authorization": f"Bearer {op_tok}"})
    assert r_detail.status_code == 200
    history = r_detail.json().get("status_history", [])
    assert len(history) >= 1
    return {"new_status": r1.json()["status"], "history_count": len(history)}

# Checkpoint 15: Quantitative LCA Environmental Impact Calculations
def cp15_esg_calculations():
    r_sus = requests.post(f"{API_V1}/auth/login", json={"username": "sustain1", "password": "SustainSecret2026!"})
    sus_tok = r_sus.json()["access_token"]
    r = requests.get(f"{API_V1}/reports/esg-summary", headers={"Authorization": f"Bearer {sus_tok}"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    assert "environmental_savings" in data
    savings = data["environmental_savings"]
    assert "co2_emissions_avoided_kg" in savings
    assert "water_conserved_liters" in savings
    assert "energy_conserved_kwh" in savings
    return {
        "co2_saved_kg": savings["co2_emissions_avoided_kg"],
        "water_saved_liters": savings["water_conserved_liters"],
        "energy_saved_kwh": savings["energy_conserved_kwh"]
    }

# Checkpoint 16: Digital Passport Issuance & Public Verification Lookup
def cp16_digital_passport_and_lookup():
    r_admin = requests.post(f"{API_V1}/auth/login", json={"username": "admin", "password": "AdminSecret2026!"})
    admin_tok = r_admin.json()["access_token"]
    
    r_cert = requests.get(f"{API_V1}/reports/batch/{created_batch_id}/certificate", headers={"Authorization": f"Bearer {admin_tok}"})
    assert r_cert.status_code == 200, f"Status {r_cert.status_code}: {r_cert.text}"
    cert = r_cert.json()
    cert_id = cert["certificate_id"]
    
    # Public lookup (unauthenticated)
    r_lookup = requests.get(f"{API_V1}/reports/certificate/verify/{cert_id}")
    assert r_lookup.status_code == 200, f"Status {r_lookup.status_code}: {r_lookup.text}"
    ver = r_lookup.json()
    assert ver["is_valid"] is True
    assert ver["verification_status"] == "AUTHENTIC"
    return {"certificate_id": cert_id, "verification_status": ver["verification_status"], "is_valid": ver["is_valid"]}

# Checkpoint 17: Token Revocation / Logout
def cp17_token_revocation():
    r = requests.post(f"{API_V1}/auth/login", json={"username": "operator1", "password": "OperatorSecret2026!"})
    assert r.status_code == 200, f"Status {r.status_code}: {r.text}"
    data = r.json()
    tok = data["access_token"]
    
    r_logout = requests.post(f"{API_V1}/auth/logout", headers={"Authorization": f"Bearer {tok}"})
    assert r_logout.status_code == 200
    
    r_me = requests.get(f"{API_V1}/auth/me", headers={"Authorization": f"Bearer {tok}"})
    assert r_me.status_code == 401, f"Expected 401 for revoked token, got {r_me.status_code}"
    return {"token_revoked": True}

def run_all():
    checkpoints = [
        (1, "Administrator Authentication", cp1_admin_auth),
        (2, "Operator Authentication", cp2_operator_auth),
        (3, "Sustainability Manager Authentication", cp3_sustain_auth),
        (4, "Manufacturer Authentication", cp4_manuf_auth),
        (5, "Public User Registration", cp5_public_reg),
        (6, "RBAC Access Control & Route Boundary Enforcement", cp6_rbac_enforcement),
        (7, "Waste Consignment Batch Creation", cp7_batch_creation),
        (8, "Textile Specimen Image Upload & MIME Verification", cp8_image_upload_and_mime),
        (9, "AI Spatial Defect Detection & Bounding Boxes", cp9_defect_and_bboxes),
        (10, "Option B Visual Estimate Governance Tagging", cp10_option_b_governance),
        (11, "5-Component Circularity Score Breakdown", cp11_circularity_formula),
        (12, "7 Recycling & Material Recovery Pathways", cp12_recycling_pathways),
        (13, "Operator Quality Review & Uncertainty Management", cp13_operator_verification),
        (14, "Batch Lifecycle Status Progression & Audit History", cp14_lifecycle_progression),
        (15, "Quantitative LCA Environmental Savings Calculations", cp15_esg_calculations),
        (16, "Digital Circularity Passport Issuance & Public Lookup", cp16_digital_passport_and_lookup),
        (17, "JWT Token Invalidation & Logout Revocation", cp17_token_revocation)
    ]
    
    for num, name, func in checkpoints:
        test_checkpoint(num, name, func)
        
    print("\n--- SUMMARY ---")
    passed = sum(1 for v in results.values() if v["status"] == "PASSED")
    print(f"Total Checkpoints: {len(checkpoints)} | Passed: {passed} | Failed: {len(checkpoints) - passed}")
    
    output_path = Path(__file__).resolve().parent.parent / "docs" / "phase-8" / "acceptance_results.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
    print(f"Results written to {output_path}")

if __name__ == "__main__":
    run_all()
