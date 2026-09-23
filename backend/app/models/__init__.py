"""Importing this package registers every model on Base.metadata.

Alembic's env.py imports it so autogenerate sees all tables; anything that
needs the full mapper configuration (e.g. string-based relationship targets)
should import from here too.
"""

from app.models.album import Album, AlbumStatus
from app.models.audit_log import AuditLog
from app.models.batch import Batch, BatchMembership, BatchRole
from app.models.photo import Photo, PhotoLike
from app.models.story import Story, StoryLike
from app.models.token_blacklist import TokenBlacklist
from app.models.user import User

__all__ = [
    "Album",
    "AlbumStatus",
    "AuditLog",
    "Batch",
    "BatchMembership",
    "BatchRole",
    "Photo",
    "PhotoLike",
    "Story",
    "StoryLike",
    "TokenBlacklist",
    "User",
]
