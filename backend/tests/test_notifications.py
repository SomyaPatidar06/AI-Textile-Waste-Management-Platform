import pytest


def get_token(client, username, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    return resp.json()["access_token"]


def test_in_app_notifications_lifecycle(client):
    op_token = get_token(client, "testoperator", "OperatorPass123!")
    rec_token = get_token(client, "testrecycler", "RecyclerPass123!")

    # Creating a batch triggers an automatic notification for the operator
    client.post(
        "/api/v1/batches",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"batch_code": "NOTIF-TEST-01", "weight_kg": 55.0, "source_type": "Post-Consumer"}
    )

    # Operator checks notifications
    notif_resp = client.get(
        "/api/v1/notifications",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert notif_resp.status_code == 200
    notifications = notif_resp.json()
    assert len(notifications) >= 1
    target_notif = notifications[0]
    assert target_notif["is_read"] is False
    notif_id = target_notif["id"]

    # Check unread count
    count_resp = client.get(
        "/api/v1/notifications/unread-count",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert count_resp.status_code == 200
    assert count_resp.json()["unread_count"] >= 1

    # Cross-user access check: Recycler attempts to read Operator's notification
    cross_resp = client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {rec_token}"}
    )
    assert cross_resp.status_code == 403
    assert "not authorized" in cross_resp.json()["detail"].lower()

    # Operator marks notification as read
    read_resp = client.patch(
        f"/api/v1/notifications/{notif_id}/read",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert read_resp.status_code == 200
    assert read_resp.json()["is_read"] is True

    # Operator deletes notification
    del_resp = client.delete(
        f"/api/v1/notifications/{notif_id}",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert del_resp.status_code == 204
