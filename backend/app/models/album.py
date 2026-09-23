import enum
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    CheckConstraint,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Text,
    extract,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.batch import Batch
    from app.models.photo import Photo
    from app.models.story import Story
    from app.models.user import User


class AlbumStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    # Albums are never row-DELETEd; "deleted" is a status flip. Because the
    # row stays, the DB's ON DELETE CASCADE to photos/stories never fires --
    # the app must hard-delete an album's photos and stories itself when
    # setting this status.
    deleted = "deleted"


class Album(CreatedAtMixin, Base):
    __tablename__ = "albums"
    __table_args__ = (
        # Postgres's default name for an unnamed table CHECK is "<table>_check";
        # naming it explicitly keeps Alembic and the DDL in agreement.
        CheckConstraint("date_end IS NULL OR date_end >= date_start", name="albums_check"),
        Index("idx_albums_batch_status", "batch_id", "status"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    batch_id: Mapped[int] = mapped_column(ForeignKey("batches.id"))
    title: Mapped[str] = mapped_column(Text)
    date_start: Mapped[date] = mapped_column(Date)
    # NULL (or equal to date_start) means a single-day album.
    date_end: Mapped[date | None] = mapped_column(Date)
    status: Mapped[AlbumStatus] = mapped_column(
        Enum(AlbumStatus, name="album_status", values_callable=lambda e: [m.value for m in e]),
        server_default=AlbumStatus.pending.value,
    )
    # The proposing member.
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    # Latest reviewer and when, for the CURRENT status (full history is in
    # audit_log). Reviewer must hold batch_admin -- app-layer check.
    reviewed_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    batch: Mapped["Batch"] = relationship(back_populates="albums")
    # Two FKs point at users, so each relationship must say which one it uses.
    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    reviewer: Mapped["User | None"] = relationship(foreign_keys=[reviewed_by])

    # photos.album_id / stories.album_id are ON DELETE CASCADE in the DB.
    # passive_deletes=True lets Postgres do that cascade instead of the ORM
    # SELECTing every child just to DELETE it one by one. "delete-orphan"
    # means removing a photo from album.photos deletes it (album_id is
    # NOT NULL, so a photo can't exist without an album anyway).
    photos: Mapped[list["Photo"]] = relationship(
        back_populates="album", cascade="all, delete-orphan", passive_deletes=True
    )
    stories: Mapped[list["Story"]] = relationship(
        back_populates="album", cascade="all, delete-orphan", passive_deletes=True
    )


# Expression index for the "on this day, years ago" timeline query:
#   WHERE EXTRACT(MONTH FROM date_start) = :m AND EXTRACT(DAY FROM date_start) = :d
# A plain index on date_start can't serve a month+day match across years.
# It's declared after the class because it needs the real Album.date_start
# column object (a plain "date_start" string here would be a string literal,
# not a column reference); an Index built from table columns attaches to that
# table automatically.
Index(
    "idx_albums_month_day",
    extract("month", Album.date_start),
    extract("day", Album.date_start),
)
