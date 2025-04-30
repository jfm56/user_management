import os
import sys
from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure the parent directory of alembic is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Safe to import app modules after path set
from app.models.user_model import Base
from settings.config import settings

# Alembic Config object
config = context.config

# Use psycopg2 for Alembic (sync engine), not asyncpg
sync_url = settings.get_resolved_database_url().replace("asyncpg", "psycopg2")
config.set_main_option("sqlalchemy.url", sync_url)

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Target metadata for autogenerate
target_metadata = Base.metadata

def run_migrations_offline():
    """Run migrations in offline mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in online mode."""
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()

# Choose offline or online mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
