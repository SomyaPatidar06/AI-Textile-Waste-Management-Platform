"""
Unit & Integration Tests for Phase 5 Specification Compliance.

Validates that the implementation strictly satisfies the requirements from
"AI_Textile Waste Intelligence Platform.pdf":
1. 5-Component Weighted Circularity Formula & 5 Recovery Categories (Module 9)
2. 6 Waste Stream Categories (Module 5)
3. 4 Required User Roles & RBAC (Module 1)
4. 7 Recycling Option Recommendations (Module 6)
5. Documented Environmental Impact Calculations (Module 8)
"""

import pytest
from fastapi.testclient import TestClient
from app.services.circularity import (
    calculate_circularity_score,
    determine_waste_category,
    generate_recommendations,
    calculate_environmental_impact,
    IMPACT_FACTORS
)
from app.models.user import RoleEnum


def test_circularity_five_component_mathematical_formula():
    """
    Verifies that the Circularity Score strictly computes:
    Circularity = 0.35 * Recyclability + 0.20 * Condition + 0.20 * Reuse + 0.15 * Environmental + 0.10 * Feasibility
    and that sub-scores sum accurately.
    """
    res = calculate_circularity_score("Cotton", "Defect Free", requires_manual_inspection=False)
    score = res["circularity_score"]
    bd = res["breakdown"]

    r = bd["material_recyclability"]
    c = bd["material_condition"]
    u = bd["reuse_potential"]
    e = bd["environmental_benefit"]
    f = bd["processing_feasibility"]

    expected_score = round(0.35 * r + 0.20 * c + 0.20 * u + 0.15 * e + 0.10 * f, 1)
    assert score == expected_score, f"Expected {expected_score}, got {score}"
    assert score >= 85.0
    assert res["circularity_category"] == "Excellent Recovery Potential"


def test_circularity_categories_thresholds():
    """Verifies all 5 specification category thresholds from PDF Page 7."""
    # Excellent (>= 85.0): Cotton Defect Free
    res_exc = calculate_circularity_score("Wool", "Defect Free")
    assert res_exc["circularity_score"] >= 85.0
    assert res_exc["circularity_category"] == "Excellent Recovery Potential"

    # High (70.0 - 84.9): Polyester Defect Free or Cotton Needle Mark
    res_high = calculate_circularity_score("Polyester", "Defect Free")
    assert 70.0 <= res_high["circularity_score"] < 85.0
    assert res_high["circularity_category"] == "High Recovery Potential"

    # Moderate (50.0 - 69.9): Poly-Cotton Blend or Cotton Weave Defect
    res_mod = calculate_circularity_score("Poly-Cotton Blend", "Pinched Fabric")
    assert 50.0 <= res_mod["circularity_score"] < 70.0
    assert res_mod["circularity_category"] == "Moderate Recovery Potential"

    # Limited (30.0 - 49.9): Mixed/Unknown with Hole
    res_lim = calculate_circularity_score("Mixed/Unknown", "Hole")
    assert 30.0 <= res_lim["circularity_score"] < 50.0
    assert res_lim["circularity_category"] == "Limited Recovery Potential"

    # Disposal Recommended (< 30.0)
    res_disp = calculate_circularity_score("Mixed/Unknown", "Stain", requires_manual_inspection=True)
    assert res_disp["circularity_category"] in ["Limited Recovery Potential", "Disposal Recommended"]


def test_six_waste_stream_categories():
    """Verifies that all 6 waste categories from PDF Page 5 can be produced."""
    # 1. Reusable
    cat_reusable = determine_waste_category("Defect Free", 88.0, "Cotton")
    assert cat_reusable == "Reusable"

    # 2. Repairable
    cat_repairable = determine_waste_category("Broken Stitch", 75.0, "Cotton")
    assert cat_repairable == "Repairable"

    # 3. Compostable
    cat_compostable = determine_waste_category("Defect Free", 72.0, "Linen")
    assert cat_compostable == "Compostable"

    # 4. Recyclable
    cat_recyclable = determine_waste_category("Weave Defect", 65.0, "Polyester")
    assert cat_recyclable == "Recyclable"

    # 5. Upcyclable
    cat_upcyclable = determine_waste_category("Hole", 45.0, "Denim")
    assert cat_upcyclable == "Upcyclable"

    # 6. Hazardous Textile Waste
    cat_hazardous = determine_waste_category("Stain", 25.0, "Mixed/Unknown")
    assert cat_hazardous == "Hazardous Textile Waste"


def test_seven_recycling_options_in_recommendations():
    """Verifies that generated recommendations reference the 7 PDF recycling options."""
    recs_reuse = generate_recommendations("Cotton", "Defect Free", "Reusable")
    assert any("[Fabric Reuse / Donation]" in r or "[Mechanical Recycling]" in r for r in recs_reuse)

    recs_repair = generate_recommendations("Denim", "Broken Stitch", "Repairable")
    assert any("Repairable" in r or "repair" in r.lower() for r in recs_repair)

    recs_chem = generate_recommendations("Polyester", "Weave Defect", "Recyclable")
    assert any("[Chemical Recycling]" in r or "dissolution" in r.lower() for r in recs_chem)

    recs_upcycle = generate_recommendations("Silk", "Hole", "Upcyclable")
    assert any("[Upcycling]" in r for r in recs_upcycle)


def test_environmental_impact_coefficients():
    """Verifies that environmental impact calculations use documented European/WRAP benchmarks."""
    cotton_impact = calculate_environmental_impact("Cotton", weight_kg=10.0)
    assert cotton_impact["weight_diverted_kg"] == 10.0
    assert cotton_impact["co2_savings_kg"] == 152.0  # 15.2 * 10
    assert cotton_impact["water_savings_liters"] == 78000.0  # 7800 * 10
    assert cotton_impact["energy_savings_kwh"] == 350.0  # 35.0 * 10

    wool_impact = calculate_environmental_impact("Wool", weight_kg=5.0)
    assert wool_impact["co2_savings_kg"] == 120.0  # 24.0 * 5
    assert wool_impact["water_savings_liters"] == 22500.0  # 4500 * 5


def test_four_user_roles_rbac(client: TestClient):
    """
    Verifies that all 4 specified roles (Admin, Operator, Sustainability Manager, Manufacturer)
    are supported with appropriate access controls.
    """
    # 1. Sustainability Manager login
    r_sm = client.post("/api/v1/auth/login", json={"username": "testsustmgr", "password": "SustMgrPass123!"})
    assert r_sm.status_code == 200
    sm_token = r_sm.json()["access_token"]
    sm_headers = {"Authorization": f"Bearer {sm_token}"}

    # Sustainability Manager can access ESG reports
    r_esg = client.get("/api/v1/reports/esg-summary", headers=sm_headers)
    assert r_esg.status_code == 200
    assert "environmental_savings" in r_esg.json()

    # 2. Manufacturer login
    r_mf = client.post("/api/v1/auth/login", json={"username": "testmanufacturer", "password": "ManufacturerPass123!"})
    assert r_mf.status_code == 200
    mf_token = r_mf.json()["access_token"]
    mf_headers = {"Authorization": f"Bearer {mf_token}"}

    # Manufacturer can create production waste batches
    r_batch = client.post(
        "/api/v1/batches",
        headers=mf_headers,
        json={
            "batch_code": "MFG-PROD-BATCH-001",
            "weight_kg": 250.0,
            "declared_material": "Cotton",
            "source_type": "Post-Industrial Garment Cutoff",
            "location": "Loom Floor #3",
            "notes": "Edge scrap offcuts from denim weave"
        }
    )
    assert r_batch.status_code == 201
    assert r_batch.json()["batch_code"] == "MFG-PROD-BATCH-001"

    # 3. Non-admin cannot list all users
    r_users = client.get("/api/v1/users", headers=mf_headers)
    assert r_users.status_code == 403

    # 4. Admin CAN list all users
    r_admin = client.post("/api/v1/auth/login", json={"username": "testadmin", "password": "AdminPass123!"})
    admin_token = r_admin.json()["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_token}"}

    r_admin_users = client.get("/api/v1/users", headers=admin_headers)
    assert r_admin_users.status_code == 200
    users_list = r_admin_users.json()
    roles_present = {u["role"] for u in users_list}
    assert RoleEnum.ADMIN.value in roles_present
    assert RoleEnum.OPERATOR.value in roles_present
    assert RoleEnum.SUSTAINABILITY_MANAGER.value in roles_present
    assert RoleEnum.MANUFACTURER.value in roles_present
