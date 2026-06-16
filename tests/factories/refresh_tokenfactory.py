from datetime import datetime, timezone, timedelta
from app.models.refresh_token import RefreshToken


class RefreshTokenFactory:
    @staticmethod
    def build(user_id: int, token: str, expires_at: datetime | None = None, revoked: bool = False) -> RefreshToken:
        if expires_at is None:
            expires_at = datetime.now(timezone.utc) + timedelta(days=7)
        return RefreshToken(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=revoked,
        )

    @staticmethod
    async def create(db, user_id: int, token: str, expires_at: datetime | None = None, revoked: bool = False):
        refresh_token = RefreshTokenFactory.build(
            user_id=user_id,
            token=token,
            expires_at=expires_at,
            revoked=revoked,
        )
        db.add(refresh_token)
        await db.commit()
        await db.refresh(refresh_token)
        return refresh_token
