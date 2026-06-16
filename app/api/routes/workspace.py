from fastapi import APIRouter, Depends, Path, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.workspace_schema import (
    CreateWorkspaceRequest,
    WorkspaceResponse,
    WorkspaceListResponse,
    UpdateWorkspaceRequest,
    MessageResponse,
)
from app.core.dependencies import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.workspace import WorkspaceService

router = APIRouter(prefix="/api", tags=["Workspace"])

@router.post("/workspace", response_model=WorkspaceResponse, status_code=status.HTTP_201_CREATED)
async def create_workspace(data: CreateWorkspaceRequest, user: User = Depends(get_current_user),  db: AsyncSession = Depends(get_db)):
    workspace = await WorkspaceService.create_workspace(data.name, user.id, db)
    return WorkspaceResponse(id=workspace.id, name=workspace.name)

@router.get("/workspaces", response_model=WorkspaceListResponse, status_code=status.HTTP_200_OK)
async def get_workspaces(user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    workspaces = await WorkspaceService.get_workspaces_by_user_id(user.id, db)
    return WorkspaceListResponse(workspaces=[WorkspaceResponse(id=workspace.id, name=workspace.name) for workspace in workspaces])

@router.get("/workspace/{workspace_id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK)
async def get_workspace(
    workspace_id: int = Path(..., ge=1, description="The ID of the workspace to retrieve"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await WorkspaceService.get_workspace(workspace_id, user.id, db)
    return WorkspaceResponse(id=workspace.id, name=workspace.name)

@router.put("/workspace/{workspace_id}", response_model=WorkspaceResponse, status_code=status.HTTP_200_OK)
async def update_workspace(
    data: UpdateWorkspaceRequest,
    workspace_id: int = Path(..., ge=1, description="The ID of the workspace to update"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    workspace = await WorkspaceService.update_workspace(workspace_id, user.id, data.name, db)
    return WorkspaceResponse(id=workspace.id, name=workspace.name)

@router.delete("/workspace/{workspace_id}", response_model=MessageResponse, status_code=status.HTTP_200_OK)
async def delete_workspace(
    workspace_id: int = Path(..., ge=1, description="The ID of the workspace to delete"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await WorkspaceService.delete_workspace(workspace_id, user.id, db)
    return MessageResponse(message="Workspace deleted successfully")
