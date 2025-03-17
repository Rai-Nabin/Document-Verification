"""
File Path: app/db/migrations/env.py
"""

from logging.config import fileConfig

from alembic import context
from app.core import settings
from app.db import Base, db_manager
from app.db.models import AuditLog, Document, User, Verification  # noqa

# Alembic Config
config = context.config

# Setup Logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for Autogenerate
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    context.configure(
        url=settings.DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    db_manager.init()

    with db_manager.engine.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
