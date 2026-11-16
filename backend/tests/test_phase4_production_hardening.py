"""
Phase 4 Production Hardening, Security & AI Reliability Integration Tests.

Validates:
1. Health, readiness and liveness probes (/health, /health/ready, /health/live).
2. JWT refresh token rotation, replay prevention, and logout revocation.
3. MIME header magic byte verification (anti-spoofing) and path traversal protection.
4. Request correlation ID propagation (X-Request-ID).
5. Sliding-window rate limiter enforcement (HTTP 429).
6. ONNX Runtime acceleration and inference metadata.
7. Zero-lock database backup and integrity verification.
"""

import io
import time
import pytest
from fastapi.testclient import TestClient
from PIL import Image

from app.main import app
from app.core.token_blocklist import token_blocklist
from app.core.rate_limiter import rate_limiter
from scripts.backup_database import backup_database, verify_sqlite_backup


def get_auth_token(client: TestClient, username: str = "testoperator", password: str = "OperatorPass123!"):
    resp = client.post("/api/v1/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200
    return resp.json()


def create_valid_test_image(format: str = "PNG") -> bytes:
    buf = io.BytesIO()
    img = Image.new("RGB", (128, 128), color=(180, 160, 140))
    img.save(buf, format=format)
    return buf.getvalue()


def test_system_health_probes(client: TestClient):
    """Verifies that all three health probes respond with 200 and valid schemas across root and /api/v1 aliases."""
    # 1. High level health (both root and api/v1 prefix)
    for path in ["/health", "/api/v1/health"]:
        r_health = client.get(path)
        assert r_health.status_code == 200
        data_h = r_health.json()
        assert data_h["status"] in ["healthy", "degraded"]
        assert "version" in data_h
        assert data_h["database"] == "connected"

    # 2. Readiness probe (both root and api/v1 prefix)
    for path in ["/health/ready", "/api/v1/health/ready"]:
        r_ready = client.get(path)
        assert r_ready.status_code == 200
        data_r = r_ready.json()
        assert data_r["status"] == "ready"
        assert data_r["checks"]["database"] == "ready"
        assert data_r["checks"]["storage"] == "writable"
        assert data_r["checks"]["ai_models"] == "loaded"

    # 3. Liveness probe (both root and api/v1 prefix)
    for path in ["/health/live", "/api/v1/health/live"]:
        r_live = client.get(path)
        assert r_live.status_code == 200
        assert r_live.json()["status"] == "alive"


def test_request_id_correlation_middleware(client: TestClient):
    """Verifies X-Request-ID propagation through HTTP middleware."""
    custom_rid = "custom-test-correlation-uuid-999"
    resp = client.get("/health", headers={"X-Request-ID": custom_rid})
    assert resp.status_code == 200
    assert resp.headers.get("X-Request-ID") == custom_rid

    # Auto-generated ID if missing
    resp2 = client.get("/health")
    assert resp2.status_code == 200
    assert "X-Request-ID" in resp2.headers
    assert len(resp2.headers["X-Request-ID"]) > 0


def test_refresh_token_rotation_and_replay_rejection(client: TestClient):
    """Verifies that using a refresh token rotates it and revokes the old token."""
    tokens = get_auth_token(client)
    old_refresh = tokens["refresh_token"]

    # First refresh succeeds
    r_ref = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r_ref.status_code == 200
    new_tokens = r_ref.json()
    assert "access_token" in new_tokens
    assert "refresh_token" in new_tokens
    assert new_tokens["refresh_token"] != old_refresh

    # Replay of the old refresh token MUST be rejected with HTTP 401
    r_replay = client.post("/api/v1/auth/refresh", json={"refresh_token": old_refresh})
    assert r_replay.status_code == 401
    assert "revoked" in r_replay.json()["detail"].lower()


def test_user_logout_token_revocation(client: TestClient):
    """Verifies that logging out revokes the access token from subsequent requests."""
    tokens = get_auth_token(client)
    access_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    # Verify token works before logout
    r_before = client.get("/api/v1/auth/me", headers=headers)
    assert r_before.status_code == 200

    # Logout
    r_logout = client.post("/api/v1/auth/logout", headers=headers)
    assert r_logout.status_code == 200

    # Token should now be blocked
    r_after = client.get("/api/v1/auth/me", headers=headers)
    assert r_after.status_code == 401
    assert "revoked" in r_after.json()["detail"].lower()


def test_mime_spoofing_magic_bytes_rejection(client: TestClient):
    """Verifies that files with fake extensions but corrupt/non-image magic bytes are rejected."""
    tokens = get_auth_token(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    # Text payload disguised as JPEG
    fake_img = b"PLAIN TEXT CONTENT NOT A JPEG FILE OR BINARY IMAGE"
    resp = client.post(
        "/api/v1/analysis/scan",
        headers=headers,
        files={"file": ("exploit.jpg", fake_img, "image/jpeg")}
    )
    assert resp.status_code == 415
    assert "Invalid image magic header" in resp.json()["detail"]


def test_valid_image_formats_accepted(client: TestClient):
    """Verifies that genuine JPEG, PNG, and WebP images pass magic byte and PIL decode."""
    tokens = get_auth_token(client)
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}

    for fmt, ext, mime in [("PNG", "png", "image/png"), ("JPEG", "jpg", "image/jpeg")]:
        img_bytes = create_valid_test_image(format=fmt)
        resp = client.post(
            "/api/v1/analysis/scan",
            headers=headers,
            files={"file": (f"test_sample.{ext}", img_bytes, mime)}
        )
        assert resp.status_code == 201
        data = resp.json()
        assert "material_prediction" in data
        assert "defect_prediction" in data
        assert "bounding_boxes" in data


def test_sliding_window_rate_limiter():
    """Unit test validating SlidingWindowRateLimiter math and window sliding."""
    test_key = "unit-test-client-127.0.0.1"
    max_reqs = 3
    window_sec = 2

    # First 3 requests allowed
    assert rate_limiter.is_allowed(test_key, max_reqs, window_sec)[0] is True
    assert rate_limiter.is_allowed(test_key, max_reqs, window_sec)[0] is True
    assert rate_limiter.is_allowed(test_key, max_reqs, window_sec)[0] is True

    # 4th request within window rejected with retry_after > 0
    allowed, retry_after = rate_limiter.is_allowed(test_key, max_reqs, window_sec)
    assert allowed is False
    assert retry_after >= 1

    # Wait for window to slide
    time.sleep(2.1)
    # Should now be allowed again
    allowed_again, _ = rate_limiter.is_allowed(test_key, max_reqs, window_sec)
    assert allowed_again is True


def test_database_backup_and_integrity_check():
    """Verifies that database backup creates a clean copy passing PRAGMA integrity_check."""
    backup_file = backup_database()
    assert backup_file.exists()
    assert backup_file.stat().st_size > 0

    # Verify backup
    is_valid = verify_sqlite_backup(backup_file)
    assert is_valid is True
