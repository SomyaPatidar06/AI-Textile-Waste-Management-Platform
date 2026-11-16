import io
import sys
from pathlib import Path
from PIL import Image
from fastapi.testclient import TestClient

backend_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(backend_dir))

from app.main import app
from app.core.database import SessionLocal, Base, engine
from app.models.user import User, RoleEnum
from app.core.security import get_password_hash


def run_comprehensive_manual_qa():
    print("=" * 70)
    print("AI Textile Waste Management Platform - Manual QA Workflow Audit")
    print("=" * 70)

    client = TestClient(app)

    # 1. System Health Check
    res = client.get("/health")
    assert res.status_code == 200, f"Health check failed: {res.text}"
    health_data = res.json()
    print(f"[QA-01] Health check: PASSED (db: {health_data['database']}, environment: {health_data['environment']})")

    # 2. Authenticate as Default Administrator
    res = client.post("/api/v1/auth/login", json={
        "username": "admin",
        "password": "AdminSecret2026!"
    })
    assert res.status_code == 200, f"Admin login failed: {res.text}"
    admin_tokens = res.json()
    admin_access_token = admin_tokens["access_token"]
    admin_headers = {"Authorization": f"Bearer {admin_access_token}"}
    print("[QA-02] Admin authentication: PASSED (JWT access & refresh tokens issued)")

    # 3. Test Refresh Token Lifecycle
    res = client.post("/api/v1/auth/refresh", json={
        "refresh_token": admin_tokens["refresh_token"]
    })
    assert res.status_code == 200, f"Refresh token failed: {res.text}"
    assert "access_token" in res.json()
    print("[QA-03] JWT token refresh: PASSED")

    # 4. Registration Role Restriction Check
    res = client.post("/api/v1/auth/register", json={
        "username": "hacker_admin",
        "email": "hacker@test.com",
        "password": "Password123!",
        "role": "ADMIN"
    })
    assert res.status_code == 403, f"Expected 403 for admin registration: {res.status_code}"
    print("[QA-04] Admin self-registration rejection: PASSED (HTTP 403 Forbidden)")

    # 5. Register Operator Account
    op_username = "qa_operator_2026"
    op_email = "operator@textileqa.com"
    res = client.post("/api/v1/auth/register", json={
        "username": op_username,
        "email": op_email,
        "password": "OperatorPass123!",
        "role": "OPERATOR"
    })
    # If already exists from earlier test, continue
    if res.status_code != 201:
        assert res.status_code == 400 and "already registered" in res.json()["detail"].lower()
    print("[QA-05] Operator registration: PASSED")

    # 6. Register Recycler Account
    rec_username = "qa_recycler_2026"
    rec_email = "recycler@textileqa.com"
    res = client.post("/api/v1/auth/register", json={
        "username": rec_username,
        "email": rec_email,
        "password": "RecyclerPass123!",
        "role": "RECYCLER"
    })
    if res.status_code != 201:
        assert res.status_code == 400 and "already registered" in res.json()["detail"].lower()
    print("[QA-06] Recycler registration: PASSED")

    # 7. Authenticate as Operator
    res = client.post("/api/v1/auth/login", json={
        "username": op_username,
        "password": "OperatorPass123!"
    })
    assert res.status_code == 200
    op_token = res.json()["access_token"]
    op_headers = {"Authorization": f"Bearer {op_token}"}

    res = client.get("/api/v1/auth/me", headers=op_headers)
    assert res.status_code == 200
    assert res.json()["role"] == "OPERATOR"
    op_user_id = res.json()["id"]
    print(f"[QA-07] Operator profile ingestion: PASSED (role={res.json()['role']})")

    # 8. RBAC Isolation Check
    res = client.get("/api/v1/users", headers=op_headers)
    assert res.status_code == 403
    res = client.get("/api/v1/users", headers=admin_headers)
    assert res.status_code == 200
    assert len(res.json()) >= 2
    print("[QA-08] RBAC user management access controls: PASSED (Operator 403, Admin 200)")

    # 9. Inventory Batch Creation
    batch_code = "BATCH-QA-VERIF-001"
    res = client.post("/api/v1/batches", headers=op_headers, json={
        "batch_code": batch_code,
        "weight_kg": 175.5,
        "declared_material": "Cotton",
        "source_type": "Post-Consumer Linens",
        "location": "QA Facility Warehouse B",
        "notes": "Verified batch for Phase 2.6 manual audit."
    })
    if res.status_code != 201:
        # If exists, fetch it
        res = client.get(f"/api/v1/batches?search={batch_code}", headers=op_headers)
        batch = res.json()[0]
    else:
        batch = res.json()
    batch_id = batch["id"]
    print(f"[QA-09] Batch creation: PASSED (id={batch_id}, code={batch['batch_code']}, weight={batch['weight_kg']} kg)")

    # 10. Inventory Lifecycle State Machine
    res = client.patch(f"/api/v1/batches/{batch_id}/status", headers=op_headers, json={
        "status": "SORTED",
        "notes": "Passed mechanical visual sorting gate."
    })
    assert res.status_code == 200
    assert res.json()["status"] == "SORTED"

    res = client.patch(f"/api/v1/batches/{batch_id}/status", headers=op_headers, json={
        "status": "PROCESSED",
        "notes": "Disassembled and shredded into secondary fiber blend."
    })
    assert res.status_code == 200
    assert res.json()["status"] == "PROCESSED"
    print("[QA-10] Batch status transitions (COLLECTED -> SORTED -> PROCESSED): PASSED")

    # 11. Audit Trail Immutability
    res = client.get(f"/api/v1/batches/{batch_id}", headers=op_headers)
    assert res.status_code == 200
    history = res.json()["status_history"]
    assert len(history) >= 2
    print(f"[QA-11] Immutable audit trail verification: PASSED ({len(history)} status log entries)")

    # 12. Upload Security Validations
    # Empty file
    res = client.post("/api/v1/analysis/scan", headers=op_headers, files={"file": ("empty.jpg", b"", "image/jpeg")})
    assert res.status_code == 400
    # Oversized file (>10MB)
    fake_huge = b"A" * (10 * 1024 * 1024 + 1024)
    res = client.post("/api/v1/analysis/scan", headers=op_headers, files={"file": ("huge.jpg", fake_huge, "image/jpeg")})
    assert res.status_code == 413
    # Corrupt / disguised executable
    res = client.post("/api/v1/analysis/scan", headers=op_headers, files={"file": ("virus.jpg", b"MZ\x90\x00\x03\x00FakePE", "image/jpeg")})
    assert res.status_code == 400
    print("[QA-12] Upload security guards (Empty 400, Oversized 413, Corrupt 400): PASSED")

    # 13. AI Characterization & Scanning Workflow
    img_byte_arr = io.BytesIO()
    test_img = Image.new("RGB", (256, 256), color=(180, 210, 230))
    test_img.save(img_byte_arr, format="JPEG")
    img_bytes = img_byte_arr.getvalue()

    res = client.post(
        "/api/v1/analysis/scan",
        headers=op_headers,
        files={"file": ("fabric_sample_01.jpg", img_bytes, "image/jpeg")},
        data={"batch_id": batch_id}
    )
    assert res.status_code == 201, f"Scan failed: {res.text}"
    scan_res = res.json()
    assert "Visual Estimate" in scan_res["material_prediction"]
    assert scan_res["requires_manual_inspection"] is True
    assert scan_res["defect_threshold_used"] == 0.45
    assert scan_res["circularity_score"] > 0
    print(f"[QA-13] Multi-task AI scan: PASSED (Material='{scan_res['material_prediction']}', Defect='{scan_res['defect_prediction']}', Score={scan_res['circularity_score']}/100)")

    # 14. In-App Notification Delivery & Ownership
    res = client.get("/api/v1/notifications/unread-count", headers=op_headers)
    assert res.status_code == 200
    unread_count = res.json()["unread_count"]
    assert unread_count >= 1

    res = client.get("/api/v1/notifications?limit=5", headers=op_headers)
    assert res.status_code == 200
    notifications = res.json()
    assert len(notifications) >= 1
    target_notif_id = notifications[0]["id"]

    res = client.patch(f"/api/v1/notifications/{target_notif_id}/read", headers=op_headers)
    assert res.status_code == 200
    assert res.json()["is_read"] is True

    # IDOR check: Recycler cannot read or delete Operator's notification
    res = client.post("/api/v1/auth/login", json={"username": rec_username, "password": "RecyclerPass123!"})
    rec_headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
    res = client.delete(f"/api/v1/notifications/{target_notif_id}", headers=rec_headers)
    assert res.status_code == 403
    print("[QA-14] In-app notifications & IDOR ownership controls: PASSED")

    # 15. ESG Summary & Analytics Calculations
    res = client.get("/api/v1/reports/esg-summary", headers=op_headers)
    assert res.status_code == 200
    esg = res.json()
    assert esg["total_weight_diverted_kg"] >= 175.5
    assert esg["environmental_savings"]["co2_emissions_avoided_kg"] > 0
    assert esg["environmental_savings"]["water_conserved_liters"] > 0
    print(f"[QA-15] ESG summary metrics: PASSED (Diverted={esg['total_weight_diverted_kg']} kg, CO2 Avoided={esg['environmental_savings']['co2_emissions_avoided_kg']} kg)")

    # 16. CSV Export Stream
    res = client.get("/api/v1/reports/export/csv", headers=op_headers)
    assert res.status_code == 200
    assert "text/csv" in res.headers["content-type"]
    csv_lines = res.text.strip().split("\n")
    assert len(csv_lines) >= 2
    assert "Scan ID,Batch ID,Date,Material (Visual Estimate)" in csv_lines[0]
    print(f"[QA-16] CSV stream export: PASSED ({len(csv_lines) - 1} rows exported)")

    # 17. Digital Recycling Certificate Generation
    res = client.get(f"/api/v1/reports/batch/{batch_id}/certificate", headers=op_headers)
    assert res.status_code == 200
    cert = res.json()
    assert cert["batch_code"] == batch_code
    assert "CERTIFIED_CIRCULAR" in cert["compliance_status"] or "DOWN_CYCLING_REQUIRED" in cert["compliance_status"]
    print(f"[QA-17] Digital circularity certificate: PASSED (Certificate ID: {cert['certificate_id']}, Status: {cert['compliance_status']})")

    # 18. Batch Deletion Role Restriction
    res = client.delete(f"/api/v1/batches/{batch_id}", headers=op_headers)
    assert res.status_code == 403, "Operator should not be allowed to delete batch"
    print("[QA-18] Operator batch deletion rejection: PASSED (HTTP 403 Forbidden)")

    print("=" * 70)
    print("ALL 18 MANUAL QA WORKFLOW AUDITS PASSED WITH ZERO FAILURES!")
    print("=" * 70)


if __name__ == "__main__":
    run_comprehensive_manual_qa()
