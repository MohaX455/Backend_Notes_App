import asyncio
import uuid

from app.core.security import create_access_token, hash_password
from app.models.user import User
from app.models.workspace import Workspace


def create_authenticated_user(client, db):
    unique_id = uuid.uuid4().hex[:8]
    user = User(
        username=f"workspace_user_{unique_id}",
        email=f"workspace_user_{unique_id}@example.com",
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


def test_create_workspace_returns_201_when_authenticated(client, db):
    create_authenticated_user(client, db)
    payload = {"name": f"New Workspace {uuid.uuid4().hex[:6]}"}

    response = client.post("/api/workspace", json=payload)

    assert response.status_code == 201
    data = response.json()
    assert data["name"] == payload["name"]
    assert isinstance(data["id"], int)


def test_create_workspace_with_existing_name_returns_400(client, db):
    user = create_authenticated_user(client, db)
    duplicate_name = f"Existing Workspace {uuid.uuid4().hex[:6]}"

    workspace = Workspace(user_id=user.id, name=duplicate_name)
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())

    response = client.post("/api/workspace", json={"name": duplicate_name})

    assert response.status_code == 400
    assert response.json()["detail"] == "Workspace with this name already exists"


def test_get_workspaces_returns_workspace_list(client, db):
    user = create_authenticated_user(client, db)
    workspace = Workspace(user_id=user.id, name=f"List Workspace {uuid.uuid4().hex[:6]}")
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())

    response = client.get("/api/workspaces")

    assert response.status_code == 200
    data = response.json()
    assert "workspaces" in data
    assert isinstance(data["workspaces"], list)
    assert any(item["id"] == workspace.id for item in data["workspaces"])
    assert any(item["name"] == workspace.name for item in data["workspaces"])


def test_get_workspace_returns_200_when_exists(client, db):
    user = create_authenticated_user(client, db)
    workspace = Workspace(user_id=user.id, name=f"Get Workspace {uuid.uuid4().hex[:6]}")
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())

    response = client.get(f"/api/workspace/{workspace.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workspace.id
    assert data["name"] == workspace.name


def test_get_workspace_returns_404_when_not_found(client, db):
    create_authenticated_user(client, db)

    response = client.get("/api/workspace/999999")

    assert response.status_code == 404
    assert response.json()["detail"] == "Workspace not found"


def test_update_workspace_returns_200_when_success(client, db):
    user = create_authenticated_user(client, db)
    workspace = Workspace(user_id=user.id, name=f"Update Workspace {uuid.uuid4().hex[:6]}")
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())

    payload = {"name": f"Updated Workspace {uuid.uuid4().hex[:6]}"}
    response = client.put(f"/api/workspace/{workspace.id}", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == workspace.id
    assert data["name"] == payload["name"]


def test_update_workspace_with_duplicate_name_returns_400(client, db):
    user = create_authenticated_user(client, db)
    workspace_one = Workspace(user_id=user.id, name=f"Workspace One {uuid.uuid4().hex[:6]}")
    workspace_two = Workspace(user_id=user.id, name=f"Workspace Two {uuid.uuid4().hex[:6]}")
    db.add_all([workspace_one, workspace_two])

    async def commit_workspaces():
        await db.commit()
        await db.refresh(workspace_one)
        await db.refresh(workspace_two)

    asyncio.run(commit_workspaces())

    response = client.put(
        f"/api/workspace/{workspace_one.id}",
        json={"name": workspace_two.name},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Workspace with this name already exists"


def test_delete_workspace_returns_200_and_removes_workspace(client, db):
    user = create_authenticated_user(client, db)
    workspace = Workspace(user_id=user.id, name=f"Delete Workspace {uuid.uuid4().hex[:6]}")
    db.add(workspace)

    async def commit_workspace():
        await db.commit()
        await db.refresh(workspace)

    asyncio.run(commit_workspace())

    response = client.delete(f"/api/workspace/{workspace.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Workspace deleted successfully"

    async def get_deleted():
        return await db.get(Workspace, workspace.id)

    deleted_workspace = asyncio.run(get_deleted())
    assert deleted_workspace is None


def test_workspace_routes_require_authentication(client):
    response = client.post("/api/workspace", json={"name": "NoAuth"})

    assert response.status_code == 401
