from datetime import UTC, datetime, timedelta

import jwt

from app.core.config import settings


def register_user(client, role="student"):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Test Account",
            "email": f"{role}.account@example.com",
            "password": "StrongPassword123!",
            "role": role,
        },
    )
    assert response.status_code == 201
    return response.json()


def login_user(client, email="student.account@example.com"):
    return client.post(
        "/auth/login",
        json={"email": email, "password": "StrongPassword123!"},
    )


def test_register_and_login(client):
    register_user(client)
    response = login_user(client)
    assert response.status_code == 200
    data = response.json()
    assert data["token_type"] == "bearer"
    assert data["expires_in"] == 900
    assert data["refresh_expires_in"] == 14 * 86400
    assert data["access_token"]
    assert data["refresh_token"]


def test_wrong_password_is_rejected(client):
    register_user(client)
    response = client.post(
        "/auth/login",
        json={
            "email": "student.account@example.com",
            "password": "IncorrectPassword123!",
        },
    )
    assert response.status_code == 401


def test_me_returns_authenticated_user(client):
    register_user(client)
    tokens = login_user(client).json()
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "student"


def test_expired_access_token_is_rejected(client):
    register_user(client)
    expired_token = jwt.encode(
        {
            "sub": "1",
            "iat": datetime.now(UTC) - timedelta(minutes=20),
            "exp": datetime.now(UTC) - timedelta(minutes=1),
            "type": "access",
        },
        settings.jwt_secret_key.get_secret_value(),
        algorithm="HS256",
    )
    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {expired_token}"},
    )
    assert response.status_code == 401


def test_refresh_rotation_and_logout_revoke_token(client):
    register_user(client)
    initial = login_user(client).json()

    refreshed_response = client.post(
        "/auth/refresh",
        json={"refresh_token": initial["refresh_token"]},
    )
    assert refreshed_response.status_code == 200
    rotated = refreshed_response.json()
    assert rotated["refresh_token"] != initial["refresh_token"]

    old_token_response = client.post(
        "/auth/refresh",
        json={"refresh_token": initial["refresh_token"]},
    )
    assert old_token_response.status_code == 401

    logout_response = client.post(
        "/auth/logout",
        json={"refresh_token": rotated["refresh_token"]},
    )
    assert logout_response.status_code == 204

    revoked_response = client.post(
        "/auth/refresh",
        json={"refresh_token": rotated["refresh_token"]},
    )
    assert revoked_response.status_code == 401


def test_student_cannot_access_admin_endpoint(client):
    register_user(client, role="student")
    tokens = login_user(client).json()
    response = client.get(
        "/admin/dashboard",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 403


def test_parent_role_can_access_parent_endpoint(client):
    register_user(client, role="parent")
    tokens = login_user(client, "parent.account@example.com").json()
    response = client.get(
        "/parent/dashboard",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["role"] == "parent"


def test_public_registration_cannot_create_admin(client):
    response = client.post(
        "/auth/register",
        json={
            "full_name": "Attempted Admin",
            "email": "attacker@example.com",
            "password": "StrongPassword123!",
            "role": "admin",
        },
    )
    assert response.status_code == 422
