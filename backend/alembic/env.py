from logging.config import fileConfig

from sqlalchemy import create_engine, pool

from alembic import context

# Importing app.models registers every table on Base.metadata; without it
# autogenerate would see an empty schema and propose dropping everything.
import app.models  # noqa: F401
from app.core.config import settings
from app.db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# The URL comes from the same settings the app uses, not alembic.ini. It's
# passed straight to the engine rather than via config.set_main_option(),
# because the .ini is parsed by configparser, which treats "%" as
# interpolation syntax and would choke on URL-encoded passwords like "%40".
DATABASE_URL = settings.DATABASE_URL

# compare_type / compare_server_default make autogenerate (and `alembic check`)
# notice column type and DEFAULT changes, not just added/removed columns.
COMPARE_OPTIONS = {"compare_type": True, "compare_server_default": True}


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (`alembic upgrade head --sql`).

    Emits SQL to stdout instead of executing it; no DB connection needed.
    """
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        **COMPARE_OPTIONS,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode against a live database."""
    connectable = create_engine(DATABASE_URL, poolclass=pool.NullPool)

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, **COMPARE_OPTIONS)

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
