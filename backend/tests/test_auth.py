import pytest
from app.models.user import RoleEnum


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["database"] == "connected"
    assert "models" in data
    assert data["models"]["defect_threshold"] == 0.45


def test_login_success(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testoperator", "password": "OperatorPass123!"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_password(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "testoperator", "password": "WrongPassword!"}
    )
    assert response.status_code == 401
    assert "Incorrect username or password" in response.json()["detail"]


def test_login_unknown_user(client):
    response = client.post(
        "/api/v1/auth/login",
        json={"username": "nonexistent_user", "password": "SomePassword123!"}
    )
    assert response.status_code == 401


def test_public_register_success(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "new_operator",
            "email": "new_operator@test.com",
            "password": "SecurePassword123!",
            "role": "OPERATOR"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "new_operator"
    assert data["role"] == "OPERATOR"
    assert data["is_active"] is True
    assert "hashed_password" not in data


def test_public_register_admin_forbidden(client):
    """Strict security test: No public user may register as ADMIN."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "rogue_admin",
            "email": "rogue_admin@test.com",
            "password": "RoguePassword123!",
            "role": "ADMIN"
        }
    )
    assert response.status_code == 403
    assert "administrator self-registration is strictly forbidden" in response.json()["detail"].lower()


def test_register_duplicate_user(client):
    response = client.post(
        "/api/v1/auth/register",
        json={
            "username": "testoperator",
            "email": "another_email@test.com",
            "password": "SecurePassword123!",
            "role": "OPERATOR"
        }
    )
    assert response.status_code == 409


def test_refresh_token(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "testoperator", "password": "OperatorPass123!"}
    )
    refresh_token = login_resp.json()["refresh_token"]

    refresh_resp = client.post(
        "/api/v1/auth/refresh",
        json={"refresh_token": refresh_token}
    )
    assert refresh_resp.status_code == 200
    data = refresh_resp.json()
    assert "access_token" in data
    assert "refresh_token" in data


def test_me_authenticated(client):
    login_resp = client.post(
        "/api/v1/auth/login",
        json={"username": "testoperator", "password": "OperatorPass123!"}
    )
    token = login_resp.json()["access_token"]

    me_resp = client.get(
        "/api/v1/auth/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    assert me_resp.status_code == 200
    data = me_resp.json()
    assert data["username"] == "testoperator"
    assert data["role"] == "OPERATOR"


def test_me_unauthenticated(client):
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
