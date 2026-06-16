from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.workspace_repo import WorkspaceRepository
from app.models.workspace import Workspace


class WorkspaceService:
    @staticmethod
    async def create_workspace(name: str, user_id: int, db: AsyncSession) -> Workspace:
        existing_workspace = await WorkspaceRepository.get_workspace_by_name(
            name=name,
            user_id=user_id,
            db=db,
        )
        if existing_workspace:
            raise HTTPException(
                status_code=400,
                detail="Workspace with this name already exists",
            )

        return await WorkspaceRepository.create_workspace(
            name=name,
            user_id=user_id,
            db=db,
        )

    @staticmethod
    async def get_workspaces_by_user_id(user_id: int, db: AsyncSession) -> list[Workspace]:
        return await WorkspaceRepository.get_workspaces_by_user_id(
            user_id=user_id,
            db=db,
        )

    @staticmethod
    async def get_workspace(workspace_id: int, user_id: int, db: AsyncSession) -> Workspace:
        workspace = await WorkspaceRepository.get_workspace_by_id(
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")
        return workspace

    @staticmethod
    async def update_workspace(workspace_id: int, user_id: int, name: str, db: AsyncSession) -> Workspace:
        workspace = await WorkspaceRepository.get_workspace_by_id(
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        existing_workspace = await WorkspaceRepository.get_workspace_by_name(
            name=name,
            user_id=user_id,
            db=db,
        )
        if existing_workspace and existing_workspace.id != workspace_id:
            raise HTTPException(
                status_code=400,
                detail="Workspace with this name already exists",
            )

        return await WorkspaceRepository.update_workspace(
            workspace=workspace,
            name=name,
            db=db,
        )

    @staticmethod
    async def delete_workspace(workspace_id: int, user_id: int, db: AsyncSession) -> None:
        workspace = await WorkspaceRepository.get_workspace_by_id(
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not workspace:
            raise HTTPException(status_code=404, detail="Workspace not found")

        await WorkspaceRepository.delete_workspace(
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
