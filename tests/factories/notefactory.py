from app.models.note import Note


class NoteFactory:
    default_title = "Factory Note"
    default_content = "Factory note content"

    @staticmethod
    def build(user_id: int, workspace_id: int, title: str = default_title, content: str = default_content, is_pinned: bool = False) -> Note:
        return Note(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
            content=content,
            is_pinned=is_pinned,
        )

    @staticmethod
    async def create(db, user_id: int, workspace_id: int, title: str = default_title, content: str = default_content, is_pinned: bool = False):
        note = NoteFactory.build(
            user_id=user_id,
            workspace_id=workspace_id,
            title=title,
            content=content,
            is_pinned=is_pinned,
        )
        db.add(note)
        await db.commit()
        await db.refresh(note)
        return note
