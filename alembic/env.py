from logging.config import fileConfig
import ssl
from alembic import context
from sqlalchemy import pool, create_engine

from app.core.config import settings
from app.models.base import Base
import app.models

config = context.config

fileConfig(config.config_file_name)

target_metadata = Base.metadata

DATABASE_URL = (
    f"mysql+pymysql://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline():
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    ssl_context = ssl.create_default_context()

    connectable = create_engine(
        DATABASE_URL,
        poolclass=pool.NullPool,
        connect_args={"ssl": ssl_context},
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
            compare_server_default=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()