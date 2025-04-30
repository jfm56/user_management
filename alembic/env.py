import os
import sys

# Ensure the parent directory of alembic is in the PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context

# Now safe to import app modules
from app.models.user_model import Base  # Adjust as needed
from settings.config import settings


# Alembic Config object, which provides access to alembic.ini values
config = context.config

# Set the database URL dynamically from Pydantic settings
config.set_main_option("sqlalchemy.url", "postgresql+psycopg2://user:password@postgres/myappdb")

# Set up logging based on alembic.ini configuration
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata used for autogeneration of migration scripts
target_metadata = Base.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode, using just a URL without a live DB connection."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode, using an Engine and a DB connection."""
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

# Determine migration mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
