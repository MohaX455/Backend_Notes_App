from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.note_repo import NoteRepository
from app.models.note import Note


class NoteService:
    @staticmethod
    async def create_note(workspace_id: int, user_id: int, title: str, content: str, db: AsyncSession) -> Note:
        # Check if workspace belongs to user (this would be done in workspace service, but for now we'll assume it's validated)
        existing_note = await NoteRepository.get_note_by_title(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            db=db,
        )
        if existing_note:
            raise HTTPException(
                status_code=400,
                detail="Note with this title already exists in this workspace",
            )

        return await NoteRepository.create_note(
            workspace_id=workspace_id,
            user_id=user_id,
            title=title,
            content=content,
            db=db,
        )

    @staticmethod
    async def get_notes_by_workspace_id(workspace_id: int, user_id: int, db: AsyncSession) -> list[Note]:
        return await NoteRepository.get_notes_by_workspace_id(
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )

    @staticmethod
    async def get_note(note_id: int, workspace_id: int, user_id: int, db: AsyncSession) -> Note:
        note = await NoteRepository.get_note_by_id(
            id=note_id,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")
        return note

    @staticmethod
    async def update_note(note_id: int, workspace_id: int, user_id: int, title: str | None, content: str | None, is_pinned: bool | None, db: AsyncSession) -> Note:
        note = await NoteRepository.get_note_by_id(
            id=note_id,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        # Check for title conflicts if title is being updated
        if title is not None and title != note.title:
            existing_note = await NoteRepository.get_note_by_title(
                workspace_id=workspace_id,
                user_id=user_id,
                title=title,
                db=db,
            )

            if existing_note and existing_note.id != note_id:
                raise HTTPException(
                    status_code=400,
                    detail="Note with this title already exists in this workspace",
                )

        return await NoteRepository.update_note(
            note=note,
            db=db,
            title=title,
            content=content,
            is_pinned=is_pinned
        )

    @staticmethod
    async def delete_note(note_id: int, workspace_id: int, user_id: int, db: AsyncSession) -> None:
        note = await NoteRepository.get_note_by_id(
            id=note_id,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )
        if not note:
            raise HTTPException(status_code=404, detail="Note not found")

        await NoteRepository.delete_note(
            id=note_id,
            workspace_id=workspace_id,
            user_id=user_id,
            db=db,
        )