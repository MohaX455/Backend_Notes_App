from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repo import UserRepository
from app.repositories.token_repo import TokenRepository
from app.core.security import hash_password, verify_password, create_access_token, create_refresh_token
from jose import jwt, JWTError
from app.core.config import settings
from datetime import datetime, timezone
from app.models.user import User

class AuthService:

    @staticmethod
    async def register(db: AsyncSession, username: str, email: str, password: str) -> User:
        existing_user = await UserRepository.get_by_email(db, email)

        if existing_user:
            raise HTTPException(status_code=400, detail="Email already exists")
        
        hashed = hash_password(password)

        user = await UserRepository.create(db, {
            "username": username,
            "email": email,
            "password_hash": hashed
        })

        return user
    
    @staticmethod
    async def login(db: AsyncSession, email: str, password: str) -> tuple[str, str, User]:
        user = await UserRepository.get_by_email(db, email)

        if not user or not verify_password(password, user.password_hash): # type: ignore
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token, expires = create_refresh_token({"sub": str(user.id)})

        await TokenRepository.create(db, {
            "user_id": user.id,
            "token": refresh_token,
            "expires_at": expires
        })

        return access_token, refresh_token, user
    
    @staticmethod
    async def refresh_token(db: AsyncSession, token: str) -> tuple[str, str]:

        # 1. Decode JWT
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid token")

        # 2. Validate token type
        if payload.get("type") != "refresh":
            raise HTTPException(status_code=401, detail="Invalid token type")

        # 3. Validate sub
        user_id = payload.get("sub")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        # 4. Check DB token
        token_db = await TokenRepository.get_by_token(db, token)

        if token_db is None:
            raise HTTPException(status_code=401, detail="Token not found")

        # 5. Check revoked
        if token_db.revoked: # type: ignore
            raise HTTPException(status_code=401, detail="Token revoked")

        # 6. Check expiration
        expires_at = token_db.expires_at # type: ignore
        # Ensure expires_at is timezone-aware
        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expires_at:
            await TokenRepository.revoke(db, token)

            raise HTTPException(
                status_code=401,
                detail="Refresh token expired"
            )

        # 7. Revoke old refresh token
        await TokenRepository.revoke(db, token)

        # 8. Create new tokens
        new_access_token = create_access_token({
            "sub": str(user_id)
        })

        new_refresh_token, expires = create_refresh_token({
            "sub": str(user_id)
        })

        # 9. Store new refresh token
        await TokenRepository.create(db, {
            "user_id": int(user_id),
            "token": new_refresh_token,
            "expires_at": expires
        })

        # 10. Return tokens
        return new_access_token, new_refresh_token
        
    
    @staticmethod
    async def logout(db: AsyncSession, refresh_token: str):
        await TokenRepository.revoke(db, refresh_token)