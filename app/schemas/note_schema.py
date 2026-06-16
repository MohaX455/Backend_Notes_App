from pydantic import BaseModel, Field
from typing import List, Optional


class CreateNoteRequest(BaseModel):
    workspace_id: int = Field(..., ge=1, description="The ID of the workspace")
    title: str = Field(min_length=1, max_length=255, description="Note title must be between 1 and 255 characters")
    content: str = Field(min_length=1, description="Note content cannot be empty")


class NoteResponse(BaseModel):
    id: int
    workspace_id: int
    title: str
    content: str
    is_pinned: bool

    class Config:
        from_attributes = True


class NoteListResponse(BaseModel):
    notes: List[NoteResponse]


class UpdateNoteRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=255, description="Note title must be between 1 and 255 characters")
    content: Optional[str] = Field(None, min_length=1, description="Note content cannot be empty")
    is_pinned: Optional[bool] = None


class MessageResponse(BaseModel):
    message: str