import pytest


def get_token_for(client, username, password):
    resp = client.post(
        "/api/v1/auth/login",
        json={"username": username, "password": password}
    )
    assert resp.status_code == 200
    return resp.json()["access_token"]


def test_list_users_as_admin_allowed(client):
    admin_token = get_token_for(client, "testadmin", "AdminPass123!")
    resp = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert resp.status_code == 200
    users = resp.json()
    assert len(users) >= 3
    usernames = [u["username"] for u in users]
    assert "testadmin" in usernames
    assert "testoperator" in usernames


def test_list_users_as_operator_forbidden(client):
    op_token = get_token_for(client, "testoperator", "OperatorPass123!")
    resp = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp.status_code == 403
    assert "Operation not permitted" in resp.json()["detail"]


def test_list_users_as_recycler_forbidden(client):
    rec_token = get_token_for(client, "testrecycler", "RecyclerPass123!")
    resp = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {rec_token}"}
    )
    assert resp.status_code == 403


def test_cross_user_profile_access_blocked(client):
    admin_token = get_token_for(client, "testadmin", "AdminPass123!")
    op_token = get_token_for(client, "testoperator", "OperatorPass123!")

    # Find admin user ID
    users_resp = client.get(
        "/api/v1/users",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    admin_id = next(u["id"] for u in users_resp.json() if u["username"] == "testadmin")

    # Operator attempts to read Admin record by ID
    resp = client.get(
        f"/api/v1/users/{admin_id}",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    assert resp.status_code == 403
    assert "Access forbidden" in resp.json()["detail"]


def test_admin_can_update_user_role(client):
    admin_token = get_token_for(client, "testadmin", "AdminPass123!")
    op_token = get_token_for(client, "testoperator", "OperatorPass123!")

    # Get operator ID
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    operator_id = me_resp.json()["id"]

    # Admin promotes operator to RECYCLER
    update_resp = client.put(
        f"/api/v1/users/{operator_id}",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"role": "RECYCLER"}
    )
    assert update_resp.status_code == 200
    assert update_resp.json()["role"] == "RECYCLER"


def test_operator_cannot_escalate_own_role(client):
    op_token = get_token_for(client, "testoperator", "OperatorPass123!")
    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {op_token}"}
    )
    operator_id = me_resp.json()["id"]

    # Operator attempts to promote self to ADMIN
    update_resp = client.put(
        f"/api/v1/users/{operator_id}",
        headers={"Authorization": f"Bearer {op_token}"},
        json={"role": "ADMIN"}
    )
    assert update_resp.status_code == 403
    assert "Only administrators can modify user roles" in update_resp.json()["detail"]
