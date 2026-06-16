import asyncio
import uuid

from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.workspace import Workspace
from app.models.note import Note


def create_authenticated_user(client, db):
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"note_user_{unique_id}",
        email=f"note_user_{unique_id}@example.com",
        password_hash=hash_password("Password1"),
    )
    db.add(user)

    async def commit_user():
        await db.commit()
        await db.refresh(user)

    asyncio.run(commit_user())
    access_token = create_access_token({"sub": str(user.id)})
    client.headers.update({"Authorization": f"Bearer {access_token}"})
    return user


def create_workspace_for_user(user, db):
    unique_id = uuid.uuid4().hex[:8]
    workspace = Workspace(
        user_id=user.id,
        name=f"Test Workspace {unique_id}"
    )
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())
    return workspace


def test_create_note_returns_201_when_authenticated(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    payload = {
        "workspace_id": workspace.id,
        "title": f"New Note {uuid.uuid4().hex[:6]}",
        "content": "This is a test note content"
    }

    response = client.post("/api/notes", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["workspace_id"] == workspace.id
    assert isinstance(data["id"], int)
    assert data["is_pinned"] is False


def test_create_note_with_existing_title_returns_400(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)
    duplicate_title = f"Duplicate Note {uuid.uuid4().hex[:6]}"

    note = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=duplicate_title,
        content="Original content",
        is_pinned=False
    )
    db.add(note)

    async def commit_note():
        await db.commit()
        await db.refresh(note)

    asyncio.run(commit_note())

    payload = {
        "workspace_id": workspace.id,
        "title": duplicate_title,
        "content": "Different content"
    }

    response = client.post("/api/notes", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Note with this title already exists in this workspace"


def test_get_notes_by_workspace_returns_note_list(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    note = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"List Note {uuid.uuid4().hex[:6]}",
        content="Content for list test",
        is_pinned=True
    )
    db.add(note)

    async def commit_note():
        await db.commit()
        await db.refresh(note)

    asyncio.run(commit_note())

    response = client.get(f"/api/notes?workspace_id={workspace.id}")

    assert response.status_code == 200
    data = response.json()
    assert "notes" in data
    assert isinstance(data["notes"], list)
    assert any(item["id"] == note.id for item in data["notes"])
    assert any(item["title"] == note.title for item in data["notes"])
    assert any(item["is_pinned"] == note.is_pinned for item in data["notes"])


def test_get_note_returns_200_when_exists(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    note = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"Get Note {uuid.uuid4().hex[:6]}",
        content="Content for get test",
        is_pinned=False
    )
    db.add(note)

    async def commit_note():
        await db.commit()
        await db.refresh(note)

    asyncio.run(commit_note())

    response = client.get(f"/api/notes/{note.id}?workspace_id={workspace.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == note.title
    assert data["content"] == note.content
    assert data["workspace_id"] == workspace.id
    assert data["is_pinned"] == note.is_pinned


def test_get_note_returns_404_when_not_found(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    response = client.get(f"/api/notes/999999?workspace_id={workspace.id}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Note not found"


def test_update_note_returns_200_when_success(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    note = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"Update Note {uuid.uuid4().hex[:6]}",
        content="Original content",
        is_pinned=False
    )
    db.add(note)

    async def commit_note():
        await db.commit()
        await db.refresh(note)

    asyncio.run(commit_note())

    payload = {
        "title": f"Updated Note {uuid.uuid4().hex[:6]}",
        "content": "Updated content",
        "is_pinned": True
    }

    response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == note.id
    assert data["title"] == payload["title"]
    assert data["content"] == payload["content"]
    assert data["is_pinned"] == payload["is_pinned"]


def test_update_note_with_duplicate_title_returns_400(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    note_one = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"Note One {uuid.uuid4().hex[:6]}",
        content="Content one",
        is_pinned=False
    )
    note_two = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"Note Two {uuid.uuid4().hex[:6]}",
        content="Content two",
        is_pinned=False
    )
    db.add_all([note_one, note_two])

    async def commit_notes():
        await db.commit()
        await db.refresh(note_one)
        await db.refresh(note_two)

    asyncio.run(commit_notes())

    payload = {"title": note_two.title}

    response = client.put(f"/api/notes/{note_one.id}?workspace_id={workspace.id}", json=payload)

    assert response.status_code == 400
    assert response.json()["detail"] == "Note with this title already exists in this workspace"


def test_delete_note_returns_200_and_removes_note(client, db):
    user = create_authenticated_user(client, db)
    workspace = create_workspace_for_user(user, db)

    note = Note(
        workspace_id=workspace.id,
        user_id=user.id,
        title=f"Delete Note {uuid.uuid4().hex[:6]}",
        content="Content for delete test",
        is_pinned=False
    )
    db.add(note)

    async def commit_note():
        await db.commit()
        await db.refresh(note)

    asyncio.run(commit_note())

    response = client.delete(f"/api/notes/{note.id}?workspace_id={workspace.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Note deleted successfully"

    async def get_deleted():
        return await db.get(Note, note.id)

    deleted_note = asyncio.run(get_deleted())
    assert deleted_note is None


def test_note_routes_require_authentication(client):
    payload = {
        "workspace_id": 1,
        "title": "NoAuth Note",
        "content": "Content"
    }

    response = client.post("/api/notes", json=payload)

    assert response.status_code == 401