from pydantic import BaseModel, Field
from typing import List


class CreateWorkspaceRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Workspace name must be between 1 and 255 characters",
    )


class WorkspaceResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


class WorkspaceListResponse(BaseModel):
    workspaces: List[WorkspaceResponse]


class UpdateWorkspaceRequest(BaseModel):
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Workspace name must be between 1 and 255 characters",
    )


class MessageResponse(BaseModel):
    message: str
