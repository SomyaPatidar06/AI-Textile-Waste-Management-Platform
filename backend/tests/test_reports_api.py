import io
from PIL import Image
import pytest


def get_token(client, username, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return resp.json()["access_token"]


def create_image_file():
    buf = io.BytesIO()
    img = Image.new("RGB", (100, 100), color=(150, 150, 150))
    img.save(buf, format="JPEG")
    buf.seek(0)
    return ("fabric_report.jpg", buf, "image/jpeg")


def test_esg_summary_report(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")

    # Register batch and scan
    batch_resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "ESG-BATCH-01", "weight_kg": 250.0, "source_type": "Industrial Waste"}
    )
    batch_id = batch_resp.json()["id"]

    filename, file_data, content_type = create_image_file()
    client.post(
        "/api/v1/analysis/scan",
        headers={"Authorization": f"Bearer {op_token}"},
        data={"batch_id": batch_id},
        files={"file": (filename, file_data, content_type)}
    )

    esg_resp = client.get(
        "/api/v1/reports/esg-summary",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert esg_resp.status_code == 200
    data = esg_resp.json()
    assert data["total_batches_tracked"] >= 1
    assert data["total_weight_diverted_kg"] >= 250.0
    assert "environmental_savings" in data
    assert data["environmental_savings"]["co2_emissions_avoided_kg"] > 0
    assert data["environmental_savings"]["water_conserved_liters"] > 0


def test_export_analyses_csv(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    export_resp = client.get(
        "/api/v1/reports/export/csv",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert export_resp.status_code == 200
    assert export_resp.headers["content-type"].startswith("text/csv")
    csv_text = export_resp.text
    assert "Scan ID,Batch ID,Date,Material" in csv_text


def test_batch_recycling_certificate(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    batch_resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "CERT-BATCH-01", "weight_kg": 500.0, "source_type": "Hospitality Linen"}
    )
    batch_id = batch_resp.json()["id"]

    cert_resp = client.get(
        f"/api/v1/reports/batch/{batch_id}/certificate",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert cert_resp.status_code == 200
    cert = cert_resp.json()
    assert cert["batch_code"] == "CERT-BATCH-01"
    assert "CERTIFIED_CIRCULAR" in cert["compliance_status"] or "DOWN_CYCLING_REQUIRED" in cert["compliance_status"]
