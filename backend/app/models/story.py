from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, ForeignKey, Index, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base, CreatedAtMixin

if TYPE_CHECKING:
    from app.models.album import Album
    from app.models.photo import Photo
    from app.models.user import User


class Story(CreatedAtMixin, Base):
    """A text post on an album. Stories are listed flat, ORDER BY created_at."""

    __tablename__ = "stories"
    __table_args__ = (Index("idx_stories_album", "album_id"),)

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    album_id: Mapped[int] = mapped_column(ForeignKey("albums.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    content: Mapped[str] = mapped_column(Text)
    # Unpins automatically (SET NULL) if the photo is deleted.
    # Known gap: the DB can't enforce that the pinned photo belongs to the
    # same album as the story -- validate that in the API layer.
    pinned_photo_id: Mapped[int | None] = mapped_column(
        ForeignKey("photos.id", ondelete="SET NULL")
    )

    album: Mapped["Album"] = relationship(back_populates="stories")
    author: Mapped["User"] = relationship()
    pinned_photo: Mapped["Photo | None"] = relationship()
    likes: Mapped[list["StoryLike"]] = relationship(
        back_populates="story", cascade="all, delete-orphan", passive_deletes=True
    )


class StoryLike(CreatedAtMixin, Base):
    """User <-> Story. Unliking is a real DELETE."""

    __tablename__ = "story_likes"
    __table_args__ = (Index("idx_story_likes_user", "user_id"),)

    story_id: Mapped[int] = mapped_column(
        ForeignKey("stories.id", ondelete="CASCADE"), primary_key=True
    )
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)

    story: Mapped["Story"] = relationship(back_populates="likes")
    user: Mapped["User"] = relationship()
