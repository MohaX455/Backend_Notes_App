from app.models.workspace import Workspace


class WorkspaceFactory:
    default_name = "Factory Workspace"

    @staticmethod
    def build(user_id: int, name: str = default_name) -> Workspace:
        return Workspace(user_id=user_id, name=name)

    @staticmethod
    async def create(db, user_id: int, name: str = default_name):
        workspace = WorkspaceFactory.build(user_id=user_id, name=name)
        db.add(workspace)
        await db.commit()
        await db.refresh(workspace)
        return workspace
