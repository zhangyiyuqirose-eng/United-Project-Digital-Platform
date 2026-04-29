"""Alembic configuration for PostgreSQL migration."""

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# Import all models so Alembic can detect them
import app.models.auth  # noqa: F401
import app.models.system  # noqa: F401
import app.models.project  # noqa: F401
import app.models.business  # noqa: F401
import app.models.cost  # noqa: F401
import app.models.resource  # noqa: F401
import app.models.timesheet  # noqa: F401
import app.models.knowledge  # noqa: F401
import app.models.notify  # noqa: F401
import app.models.workflow  # noqa: F401
import app.models.audit  # noqa: F401
import app.models.quality  # noqa: F401
import app.models.file  # noqa: F401
import app.models.report  # noqa: F401

from app.models.base import Base

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_url():
    # Alembic requires a sync driver; use psycopg2 instead of asyncpg
    url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:postgres@localhost:5432/updg_db",
    )
    if url.startswith("postgresql+asyncpg"):
        url = url.replace("postgresql+asyncpg", "postgresql+psycopg2")
    return url


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = get_url()
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    cfg = config.get_section(config.config_ini_section, {})
    cfg["sqlalchemy.url"] = get_url()
    connectable = engine_from_config(cfg, poolclass=pool.NullPool)
    with connectable.connect() as conn:
        context.configure(connection=conn, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
