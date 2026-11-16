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
    img = Image.new("RGB", (200, 200), color=(180, 180, 180))
    img.save(buf, format="JPEG")
    buf.seek(0)
    return ("test_fabric.jpg", buf, "image/jpeg")


def test_scan_textile_image(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")

    # First create a batch to associate
    batch_resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "SCAN-BATCH-01", "weight_kg": 120.0, "source_type": "Post-Consumer"}
    )
    batch_id = batch_resp.json()["id"]

    # Upload and analyze image
    filename, file_data, content_type = create_image_file()
    resp = client.post(
        "/api/v1/analysis/scan",
        headers={"Authorization": f"Bearer {op_token}"},
        data={"batch_id": batch_id},
        files={"file": (filename, file_data, content_type)}
    )
    assert resp.status_code == 201
    data = resp.json()

    assert data["batch_id"] == batch_id
    assert "Visual Estimate" in data["material_prediction"]
    assert data["requires_manual_inspection"] is True
    assert data["circularity_score"] > 0
    assert data["waste_category"] in [
        "Reusable", "Repairable", "Recyclable", "Upcyclable", "Compostable", "Hazardous Textile Waste"
    ]
    assert "circularity_category" in data
    assert data["circularity_category"] in [
        "Excellent Recovery Potential", "High Recovery Potential", "Moderate Recovery Potential",
        "Limited Recovery Potential", "Disposal Recommended"
    ]
    assert "environmental_impact" in data
    assert data["environmental_impact"]["co2_savings_kg"] > 0


def test_list_and_filter_analyses(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")

    # Upload scan
    filename, file_data, content_type = create_image_file()
    client.post(
        "/api/v1/analysis/scan",
        headers={"Authorization": f"Bearer {op_token}"},
        files={"file": (filename, file_data, content_type)}
    )

    # List all
    list_resp = client.get(
        "/api/v1/analysis",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert list_resp.status_code == 200
    analyses = list_resp.json()
    assert len(analyses) >= 1

    # Filter by requires_manual_only
    filter_resp = client.get(
        "/api/v1/analysis?requires_manual_only=true",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert filter_resp.status_code == 200
    assert len(filter_resp.json()) >= 1


def test_get_metrics_summary(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    resp = client.get(
        "/api/v1/analysis/metrics/summary",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp.status_code == 200
    metrics = resp.json()
    assert "total_scans" in metrics
    assert "average_circularity" in metrics
    assert "manual_inspection_rate" in metrics
