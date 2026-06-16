from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from app.core.config import settings
import ssl

ssl_context = ssl.create_default_context()

DATABASE_URL = (
    f"mysql+aiomysql://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=True, # logs SQL (désactive en prod)
    connect_args={"ssl": ssl_context},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
