from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# pool_pre_ping checks a pooled connection is alive before handing it out,
# which avoids errors after Postgres restarts or drops idle connections.
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# expire_on_commit=False keeps attributes readable after commit (handy when
# returning an ORM object from a request handler right after committing).
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed afterwards.

    Usage: `def endpoint(db: Session = Depends(get_db)): ...`
    Committing is the caller's job; anything uncommitted is rolled back on close.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
