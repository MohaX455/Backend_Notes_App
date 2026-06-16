import asyncio
from datetime import datetime, timedelta, timezone
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from jose import JWTError
from fastapi import HTTPException

from app.services.auth_service import AuthService
from app.models.user import User


def test_register_with_existing_email_raises_400():
    mock_db = MagicMock()
    existing_user = User(
        id=1,
        username="existing",
        email="existing@example.com",
        password_hash="hash"
    )

    with patch("app.services.auth_service.UserRepository.get_by_email", new_callable=AsyncMock, return_value=existing_user):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                AuthService.register(
                    db=mock_db,
                    username="existing",
                    email="existing@example.com",
                    password="Password1"
                )
            )

    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Email already exists"


def test_register_with_new_email_creates_user():
    mock_db = MagicMock()
    created_user = User(
        id=1,
        username="newuser",
        email="newuser@example.com",
        password_hash="hash"
    )

    with patch("app.services.auth_service.UserRepository.get_by_email", new_callable=AsyncMock, return_value=None):
        with patch("app.services.auth_service.UserRepository.create", new_callable=AsyncMock, return_value=created_user) as create_mock:
            result = asyncio.run(
                AuthService.register(
                    db=mock_db,
                    username="newuser",
                    email="newuser@example.com",
                    password="Password1"
                )
            )

    assert result is created_user
    create_mock.assert_called_once()


def test_login_with_invalid_credentials_raises_401():
    mock_db = MagicMock()

    with patch("app.services.auth_service.UserRepository.get_by_email", new_callable=AsyncMock, return_value=None):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                AuthService.login(
                    db=mock_db,
                    email="missing@example.com",
                    password="Password1"
                )
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_login_with_incorrect_password_raises_401():
    mock_db = MagicMock()
    stored_user = User(
        id=1,
        username="user",
        email="user@example.com",
        password_hash="goodhash"
    )

    with patch("app.services.auth_service.UserRepository.get_by_email", new_callable=AsyncMock, return_value=stored_user):
        with patch("app.services.auth_service.verify_password", return_value=False):
            with pytest.raises(HTTPException) as exc_info:
                asyncio.run(
                    AuthService.login(
                        db=mock_db,
                        email="user@example.com",
                        password="WrongPassword"
                    )
                )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"


def test_login_with_valid_credentials_returns_tokens_and_user():
    mock_db = MagicMock()
    stored_user = User(
        id=2,
        username="valid",
        email="valid@example.com",
        password_hash="goodhash"
    )

    with patch("app.services.auth_service.UserRepository.get_by_email", new_callable=AsyncMock, return_value=stored_user):
        with patch("app.services.auth_service.verify_password", return_value=True):
            with patch("app.services.auth_service.TokenRepository.create", new_callable=AsyncMock) as token_create_mock:
                access_token, refresh_token, user = asyncio.run(
                    AuthService.login(
                        db=mock_db,
                        email="valid@example.com",
                        password="Password1"
                    )
                )

    assert isinstance(access_token, str)
    assert isinstance(refresh_token, str)
    assert user is stored_user
    token_create_mock.assert_called_once()


def test_refresh_token_with_invalid_type_raises_401():
    mock_db = MagicMock()

    with patch("app.services.auth_service.jwt.decode", return_value={"sub": "1", "type": "access"}):
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(
                AuthService.refresh_token(
                    db=mock_db,
                    token="invalidtype"
                )
            )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid token type"


def test_refresh_token_with_expired_token_raises_401_and_revokes_token():
    mock_db = MagicMock()
    expired_refresh = MagicMock()
    expired_refresh.revoked = False
    expired_refresh.expires_at = datetime.now(timezone.utc) - timedelta(days=1)

    with patch("app.services.auth_service.jwt.decode", return_value={"sub": "1", "type": "refresh"}):
        with patch("app.services.auth_service.TokenRepository.get_by_token", new_callable=AsyncMock, return_value=expired_refresh):
            with patch("app.services.auth_service.TokenRepository.revoke", new_callable=AsyncMock) as revoke_mock:
                with pytest.raises(HTTPException) as exc_info:
                    asyncio.run(
                        AuthService.refresh_token(
                            db=mock_db,
                            token="expiredtoken"
                        )
                    )

    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Refresh token expired"
    revoke_mock.assert_called_once()


def test_logout_revokes_refresh_token():
    mock_db = MagicMock()

    with patch("app.services.auth_service.TokenRepository.revoke", new_callable=AsyncMock) as revoke_mock:
        asyncio.run(
            AuthService.logout(
                db=mock_db,
                refresh_token="sometoken"
            )
        )

    revoke_mock.assert_called_once_with(mock_db, "sometoken")
