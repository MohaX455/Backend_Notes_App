import asyncio
import pytest

from app.core.security import hash_password
from app.models.user import User
from app.models.refresh_token import RefreshToken
from datetime import datetime, timezone, timedelta


class TestRegisterEdgeCases:
    def test_register_with_short_username_returns_422(self, client):
        payload = {
            "username": "ab",
            "email": "test@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_long_username_returns_422(self, client):
        payload = {
            "username": "a" * 31,
            "email": "test@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_invalid_username_pattern_returns_422(self, client):
        payload = {
            "username": "user-name",
            "email": "test@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_forbidden_username_admin_returns_422(self, client):
        payload = {
            "username": "admin",
            "email": "admin@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_forbidden_username_root_returns_422(self, client):
        payload = {
            "username": "root",
            "email": "root@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_forbidden_username_case_insensitive_returns_422(self, client):
        payload = {
            "username": "ADMIN",
            "email": "admin2@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_short_password_returns_422(self, client):
        payload = {
            "username": "user",
            "email": "test@example.com",
            "password": "Pass1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_password_missing_uppercase_returns_422(self, client):
        payload = {
            "username": "user",
            "email": "test@example.com",
            "password": "password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_password_missing_lowercase_returns_422(self, client):
        payload = {
            "username": "user",
            "email": "test@example.com",
            "password": "PASSWORD1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_password_missing_digit_returns_422(self, client):
        payload = {
            "username": "user",
            "email": "test@example.com",
            "password": "PasswordA"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_empty_username_returns_422(self, client):
        payload = {
            "username": "",
            "email": "test@example.com",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_malformed_json_returns_422(self, client):
        response = client.post("/auth/register", content="not valid json", headers={"Content-Type": "application/json"})
        assert response.status_code == 422

    def test_register_with_missing_email_returns_422(self, client):
        payload = {
            "username": "user",
            "password": "Password1"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422

    def test_register_with_missing_password_returns_422(self, client):
        payload = {
            "username": "user",
            "email": "test@example.com"
        }
        response = client.post("/auth/register", json=payload)
        assert response.status_code == 422


class TestLoginEdgeCases:
    def test_login_with_short_password_returns_422(self, client):
        payload = {
            "email": "test@example.com",
            "password": "Pass1"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 422

    def test_login_with_missing_email_returns_422(self, client):
        payload = {
            "password": "Password1"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 422

    def test_login_with_missing_password_returns_422(self, client):
        payload = {
            "email": "test@example.com"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 422

    def test_login_with_empty_email_returns_422(self, client):
        payload = {
            "email": "",
            "password": "Password1"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 422

    def test_login_with_wrong_password_returns_401(self, client, db):
        from app.models.user import User

        # Create a unique user for this test
        user = User(
            username="wrongpwduser",
            email="wrongpwduser@example.com",
            password_hash=hash_password("Password1")
        )
        db.add(user)
        asyncio.run(db.commit())

        payload = {
            "email": "wrongpwduser@example.com",
            "password": "WrongPassword1"
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 401
        assert response.json()["detail"] == "Invalid credentials"

    def test_login_with_empty_password_returns_422(self, client):
        payload = {
            "email": "test@example.com",
            "password": ""
        }
        response = client.post("/auth/login", json=payload)
        assert response.status_code == 422


class TestMeEdgeCases:
    def test_me_with_invalid_token_returns_401(self, client):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid.token.here"}
        )
        assert response.status_code == 401

    def test_me_with_expired_token_returns_401(self, client, db, user):
        from app.core.security import create_access_token
        from datetime import datetime, timezone, timedelta
        from jose import jwt
        from app.core.config import settings

        # Create an expired token manually
        to_encode = {"sub": str(user.id)}
        expire = datetime.now(timezone.utc) - timedelta(minutes=1)
        to_encode.update({"exp": expire, "type": "access"})
        expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        response = client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {expired_token}"}
        )
        assert response.status_code == 401

    def test_me_with_malformed_bearer_returns_401(self, client):
        response = client.get(
            "/auth/me",
            headers={"Authorization": "NotBearer token"}
        )
        assert response.status_code == 401


class TestRefreshEdgeCases:
    def test_refresh_with_empty_cookie_returns_401(self, client):
        client.cookies.set("refresh_token", "")
        response = client.post("/auth/refresh")
        assert response.status_code == 401
        assert "Refresh token missing" in response.json()["detail"]

    def test_refresh_with_invalid_token_string_returns_401(self, client):
        client.cookies.set("refresh_token", "notarealtoken")
        response = client.post("/auth/refresh")
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_refresh_with_access_token_instead_of_refresh_returns_401(self, client, db):
        from app.core.security import create_access_token
        from app.models.user import User

        # Create a unique user for this test
        user = User(
            username="refreshuser",
            email="refreshuser@example.com",
            password_hash=hash_password("Password1")
        )
        db.add(user)
        asyncio.run(db.commit())

        access_token = create_access_token({"sub": str(user.id)})
        client.cookies.set("refresh_token", access_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401

    def test_refresh_with_revoked_token_returns_401(self, client, db):
        from app.core.security import create_refresh_token
        from app.repositories.token_repo import TokenRepository
        from app.models.user import User

        # Create a unique user for this test
        user = User(
            username="revokeduser",
            email="revokeduser@example.com",
            password_hash=hash_password("Password1")
        )
        db.add(user)
        asyncio.run(db.commit())

        refresh_token, expires = create_refresh_token({"sub": str(user.id)})
        asyncio.run(TokenRepository.create(db, {
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": expires
        }))
        asyncio.run(TokenRepository.revoke(db, refresh_token))

        client.cookies.set("refresh_token", refresh_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401
        assert "Token revoked" in response.json()["detail"]

    def test_refresh_with_expired_token_returns_401(self, client, db):
        from jose import jwt
        from app.core.config import settings
        from app.models.refresh_token import RefreshToken
        from app.models.user import User

        # Create a unique user for this test
        user = User(
            username="expireduser",
            email="expireduser@example.com",
            password_hash=hash_password("Password1")
        )
        db.add(user)
        asyncio.run(db.commit())

        to_encode = {"sub": str(user.id)}
        expire = datetime.now(timezone.utc) - timedelta(days=1)
        to_encode.update({"exp": expire, "type": "refresh"})
        expired_token = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        token_obj = RefreshToken(
            user_id=user.id,
            token=expired_token,
            expires_at=datetime.now(timezone.utc) - timedelta(days=1),
            revoked=False
        )
        db.add(token_obj)
        asyncio.run(db.commit())

        client.cookies.set("refresh_token", expired_token)
        response = client.post("/auth/refresh")
        assert response.status_code == 401


class TestLogoutEdgeCases:
    def test_logout_without_cookie_returns_200(self, client):
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"

    def test_logout_with_invalid_token_returns_200(self, client):
        client.cookies.set("refresh_token", "invalidtoken")
        response = client.post("/auth/logout")
        assert response.status_code == 200
        assert response.json()["message"] == "Logged out successfully"
