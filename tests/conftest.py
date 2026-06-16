import asyncio

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.dependencies import get_db
from app.models.base import Base
from app.models.user import User
from app.models.workspace import Workspace
from app.models.note import Note
from app.models.refresh_token import RefreshToken
from app.core.security import hash_password, create_access_token


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def test_engine():
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        future=True,
        echo=False,
    )

    async def create_tables():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    asyncio.run(create_tables())
    yield engine
    asyncio.run(engine.dispose())


@pytest.fixture(scope="session")
def async_session_factory(test_engine):
    return async_sessionmaker(
        test_engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )


@pytest.fixture
def db(async_session_factory, event_loop):
    session = async_session_factory()

    async def cleanup_session():
        await session.close()

    try:
        yield session
    finally:
        event_loop.run_until_complete(cleanup_session())


@pytest.fixture
def client(db):
    def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


@pytest.fixture
def user(db):
    user = User(
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_password("Password1"),
    )
    db.add(user)
    
    async def commit():
        await db.commit()
        await db.refresh(user)
    
    asyncio.run(commit())
    return user


@pytest.fixture
def workspace(db, user):
    workspace = Workspace(
        user_id=user.id,
        name="Test Workspace"
    )
    db.add(workspace)
    
    async def commit():
        await db.commit()
        await db.refresh(workspace)
    
    asyncio.run(commit())
    return workspace


@pytest.fixture
def note(db, user, workspace):
    note = Note(
        user_id=user.id,
        workspace_id=workspace.id,
        title="Test Note",
        content="Content of the test note.",
        is_pinned=False,
    )
    db.add(note)
    
    async def commit():
        await db.commit()
        await db.refresh(note)
    
    asyncio.run(commit())
    return note


@pytest.fixture
def access_token(user):
    return create_access_token({"sub": str(user.id)})


@pytest.fixture
def authenticated_client(client, access_token):
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return client
