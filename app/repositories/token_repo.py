from sqlalchemy.ext.asyncio import AsyncSession
from app.models.refresh_token import RefreshToken
from sqlalchemy import and_, update, select

class TokenRepository:
    
    @staticmethod
    async def create(db: AsyncSession, data: dict) -> RefreshToken:
        token = RefreshToken(**data)
        try:
            db.add(token)
            await db.commit()
            await db.refresh(token)
        except Exception as e:
            await db.rollback()
            raise
        return token
    
    @staticmethod
    async def get_by_token(db: AsyncSession, token: str) -> RefreshToken | None:
        result = await db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )

        return result.scalar_one_or_none()

    @staticmethod
    async def revoke(db: AsyncSession, token: str) -> None:
        try:
            await db.execute(
                update(RefreshToken)
                .where(RefreshToken.token == token)
                .values(revoked=True)
            )
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise

    @staticmethod
    async def revoke_all_tokens(user_id: int, db: AsyncSession) -> None:
        try:
            await db.execute(
                update(RefreshToken)
                .where(and_(
                    RefreshToken.user_id == user_id,
                    RefreshToken.revoked == False
                ))
                .values(revoked=True)
            )
            await db.commit()
        except Exception as e:
            await db.rollback()
            raise