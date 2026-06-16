import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.token_repo import TokenRepository
from app.models.refresh_token import RefreshToken


def test_create_commits_and_returns_refresh_token():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.refresh = AsyncMock()

    expires_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    result = asyncio.run(TokenRepository.create(mock_db, {
        "user_id": 1,
        "token": "token123",
        "expires_at": expires_at
    }))

    assert isinstance(result, RefreshToken)
    assert result.user_id == 1
    assert result.token == "token123"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()
    mock_db.refresh.assert_called_once()


def test_create_rolls_back_and_raises_on_db_error():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.commit.side_effect = SQLAlchemyError("commit failed")

    expires_at = datetime(2025, 1, 1, tzinfo=timezone.utc)
    with pytest.raises(SQLAlchemyError):
        asyncio.run(TokenRepository.create(mock_db, {
            "user_id": 1,
            "token": "token123",
            "expires_at": expires_at
        }))

    mock_db.rollback.assert_called_once()


def test_get_by_token_returns_refresh_token_when_found():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_result = MagicMock()
    expected_token = RefreshToken(user_id=1, token="token123", expires_at=datetime(2025, 1, 1, tzinfo=timezone.utc))
    mock_result.scalar_one_or_none.return_value = expected_token
    mock_db.execute.return_value = mock_result

    result = asyncio.run(TokenRepository.get_by_token(mock_db, "token123"))

    assert result is expected_token


def test_revoke_commits_changes():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    asyncio.run(TokenRepository.revoke(mock_db, "token123"))

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()


def test_revoke_rolls_back_on_error():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.commit.side_effect = SQLAlchemyError("commit failed")

    with pytest.raises(SQLAlchemyError):
        asyncio.run(TokenRepository.revoke(mock_db, "token123"))

    mock_db.rollback.assert_called_once()


def test_revoke_all_tokens_commits_changes():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_db.commit = AsyncMock()

    asyncio.run(TokenRepository.revoke_all_tokens(1, mock_db))

    mock_db.execute.assert_called_once()
    mock_db.commit.assert_called_once()
