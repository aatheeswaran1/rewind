from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, DateTime, ForeignKey, Index, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base

if TYPE_CHECKING:
    from app.models.user import User


class TokenBlacklist(Base):
    """Revoked JWTs, keyed by their `jti` claim.

    Transient security bookkeeping: rows are hard-deleted by a periodic job
    once past `expires_at` (DELETE FROM token_blacklist WHERE expires_at < now()).
    """

    __tablename__ = "token_blacklist"
    __table_args__ = (Index("idx_token_blacklist_expires", "expires_at"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    jti: Mapped[str] = mapped_column(Text, unique=True)
    blacklisted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    # Mirrors the token's own expiry.
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

    user: Mapped["User"] = relationship()
