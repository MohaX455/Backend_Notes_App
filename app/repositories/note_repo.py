

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import and_, select, delete
from app.models.note import Note
from typing import List

class NoteRepository:
    @staticmethod
    async def create_note(workspace_id: int, user_id: int, title: str, content: str, db: AsyncSession) -> Note:
        note = Note(workspace_id=workspace_id, user_id=user_id, title=title, content=content)
        try:
            db.add(note)
            await db.commit()
            await db.refresh(note)
        except Exception as e:
            await db.rollback()
            raise e
        return note
    
    @staticmethod
    async def get_note_by_id(id: int, workspace_id: int, user_id: int, db: AsyncSession) -> Note | None:
        note = await db.execute(
            select(Note)
            .where(and_(
                Note.id == id,
                Note.workspace_id == workspace_id,
                Note.user_id == user_id
                )
            )
        )
        return note.scalar_one_or_none()
    
    @staticmethod
    async def get_note_by_title(workspace_id: int, user_id: int, title: str, db: AsyncSession) -> Note | None:
        note = await db.execute(
            select(Note)
            .where(and_(
                Note.title == title,
                Note.workspace_id == workspace_id,
                Note.user_id == user_id
            ))
        )
        return note.scalar_one_or_none()
    
    @staticmethod
    async def get_notes_by_workspace_id(workspace_id: int, user_id: int, db: AsyncSession) -> List[Note]:
        notes = await db.execute(
            select(Note)
            .where(and_(
                Note.workspace_id == workspace_id,
                Note.user_id == user_id
                )
            )
        )
        return list(notes.scalars().all())
    
    @staticmethod
    async def update_note(note: Note, db: AsyncSession, title: str | None = None, content: str | None = None, is_pinned: bool | None = None) -> Note:
        try:
            if title is not None:
                note.title = title
            if content is not None:
                note.content = content
            if is_pinned is not None:
                note.is_pinned = is_pinned

            await db.commit()
            await db.refresh(note)

            return note
        except Exception as e:
            await db.rollback()
            raise e

    @staticmethod
    async def delete_note(id: int, workspace_id: int, user_id: int, db: AsyncSession) -> None:
        try:
            await db.execute(
                delete(Note)
                .where(and_(
                    Note.id == id,
                    Note.workspace_id == workspace_id, 
                    Note.user_id == user_id
                    )
                )
            )
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise e

            


