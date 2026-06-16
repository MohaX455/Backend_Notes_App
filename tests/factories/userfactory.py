from app.models.user import User
from app.core.security import hash_password


class UserFactory:
    default_username = "factory_user"
    default_email = "factory_user@example.com"
    default_password = "Password1"

    @staticmethod
    def build(
        username: str = default_username,
        email: str = default_email,
        password: str = default_password,
    ) -> User:
        return User(
            username=username,
            email=email,
            password_hash=hash_password(password),
        )

    @staticmethod
    async def create(db, username: str = default_username, email: str = default_email, password: str = default_password):
        user = UserFactory.build(username=username, email=email, password=password)
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
