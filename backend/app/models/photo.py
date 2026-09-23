from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.user import User


class Photo(CreatedAtMixin, Base):
    __tablename__ = "photos"
    __table_args__ = (
        Index("idx_photos_album", "album_id"),
        Index("idx_photos_uploaded_by", "uploaded_by"),
    )

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id", ondelete="CASCADE"))
    # Used for the "members can only delete their own photos" rule.
    uploaded_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    file_path: Mapped[str] = mapped_column(Text)

    album: Mapped["Album"] = relationship(back_populates="photos")
    uploader: Mapped["User"] = relationship()
    likes: Mapped[list["PhotoLike"]] = relationship(
        back_populates="photo", cascade="all, delete-orphan", passive_deletes=True
    )
    # No relationship to stories that pin this photo: stories.pinned_photo_id
    # is ON DELETE SET NULL, which Postgres handles on its own.


class PhotoLike(CreatedAtMixin, Base):
    """User <-> Photo. Unliking is a real DELETE."""

    __tablename__ = "photo_likes"
    __table_args__ = (
        # The composite PK (photo_id, user_id) already indexes "likes on this
        # photo"; this one covers "photos this user liked".
        Index("idx_photo_likes_user", "user_id"),
    )

    photo_id: Mapped[int] = mapped_column(
        ForeignKey("photos.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    photo: Mapped["Photo"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship()
