from datetime import datetime

from sqlalchemy import DateTime, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# Constraint naming convention.
#
# Without names, SQLAlchemy leaves naming to Postgres, and Alembic can't
# reliably drop/alter an unnamed constraint later. These templates reproduce
# Postgres's own default names (users_pkey, users_email_key,
# albums_batch_id_fkey, ...) so the ORM, the migrations and the hand-written
# DDL all agree on every constraint name.
NAMING_CONVENTION = {
    "pk": "%(table_name)s_pkey",
    "uq": "%(table_name)s_%(column_0_N_name)s_key",
    "fk": "%(table_name)s_%(column_0_name)s_fkey",
    "ix": "ix_%(column_0_label)s",
}


class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)


class CreatedAtMixin:
    """Adds `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`.

    - NOT NULL comes from the `Mapped[datetime]` annotation (a non-Optional
      type); `Mapped[datetime | None]` would make it nullable.
    - `server_default` puts the default in the DB schema itself, so rows
      inserted outside the ORM (psql, other services) get it too. A Python-side
      `default=` would only apply to ORM inserts.
    - `sort_order` keeps this column last in CREATE TABLE, matching the DDL
      (mixin columns would otherwise come first).
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), sort_order=100
    )
