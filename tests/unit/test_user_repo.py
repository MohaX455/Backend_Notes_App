import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.exc import SQLAlchemyError

from app.repositories.user_repo import UserRepository
from app.models.user import User


def test_get_by_email_returns_user_when_found():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_result = MagicMock()
    expected_user = User(id=1, username="test", email="test@example.com", password_hash="hash")
    mock_result.scalar_one_or_none.return_value = expected_user
    mock_db.execute.return_value = mock_result

    result = asyncio.run(UserRepository.get_by_email(mock_db, "test@example.com"))

    assert result is expected_user
    mock_db.execute.assert_called_once()


def test_get_by_email_returns_none_when_not_found():
    mock_db = MagicMock()
    mock_db.execute = AsyncMock()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_db.execute.return_value = mock_result

    result = asyncio.run(UserRepository.get_by_email(mock_db, "missing@example.com"))

    assert result is None


def test_create_commits_and_returns_user():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    new_user = User(username="newuser", email="newuser@example.com", password_hash="hash")

    result = asyncio.run(UserRepository.create(mock_db, {
        "username": "newuser",
        "email": "newuser@example.com",
        "password_hash": "hash"
    }))

    assert isinstance(result, User)
    assert result.username == "newuser"
    assert result.email == "newuser@example.com"
    mock_db.add.assert_called_once()
    mock_db.commit.assert_called_once()


def test_create_rolls_back_and_raises_on_db_error():
    mock_db = MagicMock()
    mock_db.commit = AsyncMock()
    mock_db.rollback = AsyncMock()
    mock_db.commit.side_effect = SQLAlchemyError("failed")

    with pytest.raises(SQLAlchemyError):
        asyncio.run(UserRepository.create(mock_db, {
            "username": "erroruser",
            "email": "error@example.com",
            "password_hash": "hash"
        }))

    mock_db.rollback.assert_called_once()
