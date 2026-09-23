from typing import TYPE_CHECKING, Any

from sqlalchemy import BigInteger, ForeignKey, Index, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.user import User


class AuditLog(CreatedAtMixin, Base):
    """Moderation/admin actions only (album review, role changes, member
    removal, user (de)activation) -- not every mutation.

    Write each entry in the same transaction as the action it records.
    """

    __tablename__ = "audit_log"
    __table_args__ = (
        Index("idx_audit_log_entity", "entity_type", "entity_id"),
        Index("idx_audit_log_actor", "actor_id"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    # Nullable: reserved for future system/cron-driven actions.
    actor_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    # e.g. "album.approved", "membership.removed", "user.deactivated"
    action: Mapped[str] = mapped_column(Text)
    # "album" | "batch_membership" | "user"
    entity_type: Mapped[str] = mapped_column(Text)
    # Deliberately NOT a foreign key: batch_membership rows are hard-deleted,
    # and the log entry must outlive the row it describes.
    entity_id: Mapped[int] = mapped_column(BigInteger)
    # The DB column is called "metadata", but `metadata` is reserved on
    # declarative classes (it's Base.metadata, the schema registry). So the
    # Python attribute is `meta`, mapped onto the "metadata" column.
    meta: Mapped[dict[str, Any] | None] = mapped_column("metadata", JSONB)

    actor: Mapped["User | None"] = relationship()
