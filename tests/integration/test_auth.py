import asyncio
import pytest

from app.core.security import hash_password
from app.models.user import User


def test_register_returns_201_with_valid_payload(client):
    payload = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "Password1"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["message"] == "Registration successful"
    assert data["user"]["email"] == "newuser@example.com"


def test_register_with_existing_email_returns_400(client, db):
    user = User(
        username="existing",
        email="existing@example.com",
        password_hash=hash_password("Password1")
    )
    db.add(user)
    asyncio.run(db.commit())

    payload = {
        "username": "other",
        "email": "existing@example.com",
        "password": "Password1"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Email already exists"


def test_register_with_invalid_email_returns_422(client):
    payload = {
        "username": "newuser",
        "email": "invalid-email",
        "password": "Password1"
    }

    response = client.post("/auth/register", json=payload)

    assert response.status_code == 422


def test_login_returns_200_and_sets_cookie(client, db):
    user = User(
        username="loginuser",
        email="loginuser@example.com",
        password_hash=hash_password("Password1")
    )
    db.add(user)
    asyncio.run(db.commit())

    payload = {
        "email": "loginuser@example.com",
        "password": "Password1"
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 200
    assert response.json()["message"] == "Login successful"
    assert response.cookies.get("refresh_token") is not None
    assert response.json()["token"]["access_token"]


def test_login_with_invalid_credentials_returns_401(client):
    payload = {
        "email": "missing@example.com",
        "password": "Password1"
    }

    response = client.post("/auth/login", json=payload)

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_with_missing_cookie_returns_401(client):
    response = client.post("/auth/refresh")

    assert response.status_code == 401
    assert response.json()["detail"] == "Refresh token missing"


def test_me_with_valid_token_returns_user(client, db):
    user = User(
        username="meuser",
        email="meuser@example.com",
        password_hash=hash_password("Password1")
    )
    db.add(user)
    asyncio.run(db.commit())

    login_payload = {
        "email": "meuser@example.com",
        "password": "Password1"
    }
    login_response = client.post("/auth/login", json=login_payload)
    access_token = login_response.json()["token"]["access_token"]

    response = client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 200
    assert response.json()["email"] == "meuser@example.com"


def test_me_without_authorization_returns_401(client):
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_logout_clears_refresh_cookie(client, db):
    user = User(
        username="logoutuser",
        email="logoutuser@example.com",
        password_hash=hash_password("Password1")
    )
    db.add(user)
    asyncio.run(db.commit())

    login_payload = {
        "email": "logoutuser@example.com",
        "password": "Password1"
    }
    login_response = client.post("/auth/login", json=login_payload)
    assert login_response.cookies.get("refresh_token") is not None

    response = client.post("/auth/logout")

    assert response.status_code == 200
    assert "refresh_token=" in response.headers.get("set-cookie", "")
    assert response.json()["message"] == "Logged out successfully"
