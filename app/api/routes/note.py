from fastapi import APIRouter, Depends, Path, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.note_schema import (
    CreateNoteRequest,
    NoteResponse,
    NoteListResponse,
    UpdateNoteRequest,
    MessageResponse,
)
from app.core.dependencies import get_db
from app.core.dependencies import get_current_user
from app.models.user import User
from app.services.note_service import NoteService

router = APIRouter(prefix="/api", tags=["Notes"])

@router.post("/notes", response_model=NoteResponse, status_code=201)
async def create_note(
    data: CreateNoteRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    note = await NoteService.create_note(
        workspace_id=data.workspace_id,
        user_id=user.id,
        title=data.title,
        content=data.content,
        db=db
    )
    return NoteResponse(
        id=note.id,
        workspace_id=note.workspace_id,
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned
    )

@router.get("/notes", response_model=NoteListResponse, status_code=200)
async def get_notes_by_workspace(
    workspace_id: int = Query(..., ge=1, description="The ID of the workspace to get notes from"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    notes = await NoteService.get_notes_by_workspace_id(
        workspace_id=workspace_id,
        user_id=user.id,
        db=db
    )
    return NoteListResponse(
        notes=[
            NoteResponse(
                id=note.id,
                workspace_id=note.workspace_id,
                title=note.title,
                content=note.content,
                is_pinned=note.is_pinned
            ) for note in notes
        ]
    )

@router.get("/notes/{note_id}", response_model=NoteResponse, status_code=200)
async def get_note(
    note_id: int = Path(..., ge=1, description="The ID of the note to retrieve"),
    workspace_id: int = Query(..., ge=1, description="The ID of the workspace"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    note = await NoteService.get_note(
        note_id=note_id,
        workspace_id=workspace_id,
        user_id=user.id,
        db=db
    )
    return NoteResponse(
        id=note.id,
        workspace_id=note.workspace_id,
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned
    )

@router.put("/notes/{note_id}", response_model=NoteResponse, status_code=200)
async def update_note(
    data: UpdateNoteRequest,
    note_id: int = Path(..., ge=1, description="The ID of the note to update"),
    workspace_id: int = Query(..., ge=1, description="The ID of the workspace"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    note = await NoteService.update_note(
        note_id=note_id,
        workspace_id=workspace_id,
        user_id=user.id,
        title=data.title,
        content=data.content,
        is_pinned=data.is_pinned,
        db=db
    )
    return NoteResponse(
        id=note.id,
        workspace_id=note.workspace_id,
        title=note.title,
        content=note.content,
        is_pinned=note.is_pinned
    )

@router.delete("/notes/{note_id}", response_model=MessageResponse, status_code=200)
async def delete_note(
    note_id: int = Path(..., ge=1, description="The ID of the note to delete"),
    workspace_id: int = Query(..., ge=1, description="The ID of the workspace"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    await NoteService.delete_note(
        note_id=note_id,
        workspace_id=workspace_id,
        user_id=user.id,
        db=db
    )
    return MessageResponse(message="Note deleted successfully")