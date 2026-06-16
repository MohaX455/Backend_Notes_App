import asyncio
import uuid

from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.workspace import Workspace
from app.models.note import Note


def create_authenticated_user(client, db):
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"edge_user_{unique_id}",
        email=f"edge_user_{unique_id}@example.com",
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
        name=f"Edge Workspace {unique_id}"
    )
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())
    return workspace


class TestCreateNoteEdgeCases:
    def test_create_note_with_empty_title_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "title": "",
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_missing_title_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_long_title_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "title": "a" * 256,
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_empty_content_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "title": "Valid Title",
            "content": ""
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_missing_content_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "title": "Valid Title"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_missing_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        payload = {
            "title": "Valid Title",
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_negative_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        payload = {
            "workspace_id": -1,
            "title": "Valid Title",
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_zero_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        payload = {
            "workspace_id": 0,
            "title": "Valid Title",
            "content": "Valid content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 422

    def test_create_note_with_very_long_content_returns_201(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {
            "workspace_id": workspace.id,
            "title": "Long Content Note",
            "content": "a" * 10000
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 201
        assert len(response.json()["content"]) == 10000


class TestGetNotesEdgeCases:
    def test_get_notes_with_missing_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes")
        assert response.status_code == 422

    def test_get_notes_with_negative_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes?workspace_id=-1")
        assert response.status_code == 422

    def test_get_notes_with_zero_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes?workspace_id=0")
        assert response.status_code == 422

    def test_get_notes_from_nonexistent_workspace_returns_empty_list(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes?workspace_id=999999")
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == []

    def test_get_notes_empty_workspace_returns_empty_list(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        response = client.get(f"/api/notes?workspace_id={workspace.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["notes"] == []
        assert "notes" in data


class TestGetNoteEdgeCases:
    def test_get_note_with_missing_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes/1")
        assert response.status_code == 422

    def test_get_note_with_negative_note_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes/-1?workspace_id=1")
        assert response.status_code == 422

    def test_get_note_with_zero_note_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes/0?workspace_id=1")
        assert response.status_code == 422

    def test_get_note_with_negative_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.get("/api/notes/1?workspace_id=-1")
        assert response.status_code == 422

    def test_get_note_from_other_workspace_returns_404(self, client, db):
        user = create_authenticated_user(client, db)
        workspace1 = create_workspace_for_user(user, db)
        workspace2 = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace1.id,
            user_id=user.id,
            title="Test Note",
            content="Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        response = client.get(f"/api/notes/{note.id}?workspace_id={workspace2.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"


class TestUpdateNoteEdgeCases:
    def test_update_note_with_empty_title_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"title": ""}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 422

    def test_update_note_with_long_title_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"title": "a" * 256}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 422

    def test_update_note_with_empty_content_returns_422(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"content": ""}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 422

    def test_update_note_with_only_title_returns_200(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Original Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"title": f"Updated {uuid.uuid4().hex[:6]}"}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == payload["title"]
        assert data["content"] == "Original Content"
        assert data["is_pinned"] is False

    def test_update_note_with_only_content_returns_200(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Original Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"content": "Updated Content"}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original Title"
        assert data["content"] == "Updated Content"
        assert data["is_pinned"] is False

    def test_update_note_with_only_is_pinned_returns_200(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Original Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {"is_pinned": True}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original Title"
        assert data["content"] == "Original Content"
        assert data["is_pinned"] is True

    def test_update_note_with_empty_payload_returns_200(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace.id,
            user_id=user.id,
            title="Original Title",
            content="Original Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        payload = {}
        response = client.put(f"/api/notes/{note.id}?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == "Original Title"
        assert data["content"] == "Original Content"
        assert data["is_pinned"] is False

    def test_update_nonexistent_note_returns_404(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        payload = {"title": "New Title"}
        response = client.put(f"/api/notes/999999?workspace_id={workspace.id}", json=payload)
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"


class TestDeleteNoteEdgeCases:
    def test_delete_note_with_missing_workspace_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.delete("/api/notes/1")
        assert response.status_code == 422

    def test_delete_note_with_negative_note_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.delete("/api/notes/-1?workspace_id=1")
        assert response.status_code == 422

    def test_delete_note_with_zero_note_id_returns_422(self, client, db):
        user = create_authenticated_user(client, db)

        response = client.delete("/api/notes/0?workspace_id=1")
        assert response.status_code == 422

    def test_delete_nonexistent_note_returns_404(self, client, db):
        user = create_authenticated_user(client, db)
        workspace = create_workspace_for_user(user, db)

        response = client.delete(f"/api/notes/999999?workspace_id={workspace.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"

    def test_delete_note_from_other_workspace_returns_404(self, client, db):
        user = create_authenticated_user(client, db)
        workspace1 = create_workspace_for_user(user, db)
        workspace2 = create_workspace_for_user(user, db)

        note = Note(
            workspace_id=workspace1.id,
            user_id=user.id,
            title="Test Note",
            content="Content",
            is_pinned=False
        )
        db.add(note)

        async def commit_note():
            await db.commit()
            await db.refresh(note)

        asyncio.run(commit_note())

        response = client.delete(f"/api/notes/{note.id}?workspace_id={workspace2.id}")
        assert response.status_code == 404
        assert response.json()["detail"] == "Note not found"


class TestNoteAuthenticationEdgeCases:
    def test_create_note_without_authentication_returns_401(self, client):
        payload = {
            "workspace_id": 1,
            "title": "No Auth Note",
            "content": "Content"
        }

        response = client.post("/api/notes", json=payload)
        assert response.status_code == 401

    def test_get_notes_without_authentication_returns_401(self, client):
        response = client.get("/api/notes?workspace_id=1")
        assert response.status_code == 401

    def test_get_note_without_authentication_returns_401(self, client):
        response = client.get("/api/notes/1?workspace_id=1")
        assert response.status_code == 401

    def test_update_note_without_authentication_returns_401(self, client):
        payload = {"title": "Updated"}
        response = client.put("/api/notes/1?workspace_id=1", json=payload)
        assert response.status_code == 401

    def test_delete_note_without_authentication_returns_401(self, client):
        response = client.delete("/api/notes/1?workspace_id=1")
        assert response.status_code == 401