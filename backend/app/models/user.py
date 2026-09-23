from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.batch import BatchMembership


class User(CreatedAtMixin, Base):
    """A person. Rows are never deleted: `is_active = False` means "removed",
    and their content stays attributed to them."""

    __tablename__ = "users"

    # BigInteger + primary_key renders as BIGSERIAL on Postgres.
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    email: Mapped[str] = mapped_column(Text, unique=True)
    password_hash: Mapped[str] = mapped_column(Text)
    # System-level role, not batch-scoped (batch roles live on BatchMembership).
    is_super_admin: Mapped[bool] = mapped_column(server_default=text("false"))
    is_active: Mapped[bool] = mapped_column(server_default=text("true"))
    profile_photo_path: Mapped[str | None] = mapped_column(Text)

    # batch_memberships.user_id has no ON DELETE clause, so the DB refuses to
    # delete a user who still has memberships. passive_deletes="all" tells the
    # ORM not to "help" by nulling out user_id on loaded memberships; the DB's
    # FK error is the intended outcome.
    memberships: Mapped[list["BatchMembership"]] = relationship(
        back_populates="user", passive_deletes="all"
    )
