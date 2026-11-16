import pytest
from app.models.inventory import BatchStatusEnum


def get_token(client, username, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return resp.json()["access_token"]


def test_create_batch_success(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={
            "batch_code": "BATCH-2026-001",
            "weight_kg": 150.5,
            "declared_material": "Cotton",
            "source_type": "Post-Consumer Garments",
            "location": "Warehouse A, Bin 3",
            "notes": "Initial test batch"
        }
    )
    assert resp.status_code == 201
    data = resp.json()
    assert data["batch_code"] == "BATCH-2026-001"
    assert data["weight_kg"] == 150.5
    assert data["status"] == "COLLECTED"
    assert "id" in data


def test_create_duplicate_batch_rejected(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    # First batch
    client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "BATCH-DUP-01", "weight_kg": 50.0, "source_type": "Industrial"}
    )
    # Duplicate
    resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "BATCH-DUP-01", "weight_kg": 75.0, "source_type": "Industrial"}
    )
    assert resp.status_code == 409


def test_create_batch_negative_weight_rejected(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "BATCH-NEG-01", "weight_kg": -10.0, "source_type": "Industrial"}
    )
    assert resp.status_code == 422


def test_list_and_filter_batches(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "FILTER-01", "weight_kg": 20.0, "source_type": "Hospitality Linen"}
    )
    client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "FILTER-02", "weight_kg": 40.0, "source_type": "Denim Offcuts"}
    )

    # Filter by source_type
    resp = client.get(
        "/api/v1/batches?source_type=Hospitality",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp.status_code == 200
    batches = resp.json()
    assert len(batches) == 1
    assert batches[0]["batch_code"] == "FILTER-01"


def test_batch_status_lifecycle_and_history(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    create_resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "LIFECYCLE-01", "weight_kg": 85.0, "source_type": "Post-Consumer"}
    )
    batch_id = create_resp.json()["id"]

    # Transition to SORTED
    patch_resp = client.patch(
        f"/api/v1/batches/{batch_id}/status",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"status": "SORTED", "notes": "Sorted by optical sorter"}
    )
    assert patch_resp.status_code == 200
    data = patch_resp.json()
    assert data["status"] == "SORTED"
    assert len(data["status_history"]) >= 2
    assert data["status_history"][0]["new_status"] == "SORTED"

    # Transition to PROCESSED
    patch_resp2 = client.patch(
        f"/api/v1/batches/{batch_id}/status",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"status": "PROCESSED", "notes": "Mechanically shredded"}
    )
    assert patch_resp2.status_code == 200
    assert patch_resp2.json()["status"] == "PROCESSED"


def test_delete_batch_admin_only(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    admin_token = get_token(client, "testadmin", "AdminPass123!")

    create_resp = client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "DELETE-ME", "weight_kg": 10.0, "source_type": "Test"}
    )
    batch_id = create_resp.json()["id"]

    # Operator delete should fail (403)
    op_del_resp = client.delete(
        f"/api/v1/batches/{batch_id}",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert op_del_resp.status_code == 403

    # Admin delete should succeed (204)
    admin_del_resp = client.delete(
        f"/api/v1/batches/{batch_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert admin_del_resp.status_code == 204
