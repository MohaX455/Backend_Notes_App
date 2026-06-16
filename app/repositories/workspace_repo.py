from typing import List

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.workspace import Workspace
from sqlalchemy import and_, select, delete


class WorkspaceRepository:

    @staticmethod
    async def get_workspace_by_id(workspace_id: int, user_id: int, db: AsyncSession) -> Workspace | None:
        result = await db.execute(select(Workspace).where(and_(Workspace.id == workspace_id, Workspace.user_id == user_id)))
        return result.scalars().first()

    @staticmethod
    async def get_workspace_by_name(name: str, user_id: int, db: AsyncSession) -> Workspace | None:
        result = await db.execute(select(Workspace).where(and_(Workspace.name == name, Workspace.user_id == user_id)))
        return result.scalars().first()
    
    @staticmethod
    async def get_workspaces_by_user_id(user_id: int, db: AsyncSession) -> List[Workspace]:
        result = await db.execute(select(Workspace).where(Workspace.user_id == user_id))
        return list(result.scalars().all())

    @staticmethod
    async def create_workspace(name: str, user_id: int, db: AsyncSession) -> Workspace:
        new_workspace = Workspace(name=name, user_id=user_id)
        try:
            db.add(new_workspace)
            await db.commit()
            await db.refresh(new_workspace)
        except Exception as e:
            await db.rollback()
            raise e
        return new_workspace
    
    @staticmethod
    async def delete_workspace(workspace_id: int, user_id: int, db: AsyncSession) -> None:
        try:
            await db.execute(delete(Workspace).where(and_(Workspace.id == workspace_id, Workspace.user_id == user_id)))
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def update_workspace(
        workspace: Workspace,
        name: str,
        db: AsyncSession
    ) -> Workspace:
        try:
            workspace.name = name
            
            await db.commit()
            await db.refresh(workspace)

            return workspace

        except Exception:
            await db.rollback()
            raise