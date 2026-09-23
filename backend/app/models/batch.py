import enum
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, Enum, ForeignKey, Index, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.user import User


class BatchRole(str, enum.Enum):
    member = "member"
    batch_admin = "batch_admin"


class Batch(CreatedAtMixin, Base):
    __tablename__ = "batches"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[str] = mapped_column(Text)
    # Must be a super admin -- enforced in the app layer, not the DB.
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))

    creator: Mapped["User"] = relationship()
    # Neither FK below has ON DELETE, so deleting a batch that still has
    # memberships/albums is a DB error by design (see User.memberships).
    memberships: Mapped[list["BatchMembership"]] = relationship(
        back_populates="batch", passive_deletes="all"
    )
    albums: Mapped[list["Album"]] = relationship(back_populates="batch", passive_deletes="all")


class BatchMembership(Base):
    """User <-> Batch, carrying the user's role in that batch.

    Leaving a batch is a real DELETE; rejoining is a fresh INSERT, which is why
    a plain UNIQUE (user_id, batch_id) is safe here.
    """

    __tablename__ = "batch_memberships"
    __table_args__ = (
        UniqueConstraint("user_id", "batch_id"),
        Index("idx_batch_memberships_user", "user_id"),
        Index("idx_batch_memberships_batch", "batch_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
    # values_callable stores the enum *values* ("batch_admin") in Postgres
    # rather than the member *names*. They're identical here, but this keeps
    # the DB labels stable if a Python member is ever renamed.
    role: Mapped[BatchRole] = mapped_column(
        Enum(BatchRole, name="batch_role", values_callable=lambda e: [m.value for m in e]),
        server_default=BatchRole.member.value,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="memberships")
    batch: Mapped["Batch"] = relationship(back_populates="memberships")
