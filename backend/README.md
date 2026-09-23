# Rewind — Backend

FastAPI + SQLAlchemy 2.x + PostgreSQL + Alembic, structured as a monolith.

> **Status:** the database layer is complete (settings, engine/session, ORM models,
> initial migration). `app/api/`, `app/services/`, `app/repositories/` and
> `app/schemas/` are still empty placeholders.

## Prerequisites

- Python 3.12 with `venv` support (`sudo apt install python3.12-venv python3-pip` on Ubuntu)
- PostgreSQL (developed against 16+, tested on 18)

## First-time setup

Run everything from `backend/`.

```bash
# 1. Virtual environment + dependencies
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Environment file (gitignored), then edit it with your real DB password.
#    Special characters in the password must be URL-encoded, e.g. "@" -> "%40".
cp .env.example .env

# 3. Create the database
createdb -h localhost -U postgres rewind

# 4. Apply migrations
alembic upgrade head
```

## Everyday commands

| Task | Command |
| --- | --- |
| Activate the venv | `source venv/bin/activate` |
| Apply all migrations | `alembic upgrade head` |
| Show the current DB revision | `alembic current` |
| Show migration history | `alembic history` |
| Check models and DB are in sync | `alembic check` (should print "No new upgrade operations detected") |
| Create a migration after changing a model | `alembic revision --autogenerate -m "describe change"`, then **review the generated file** |
| Undo the last migration | `alembic downgrade -1` |
| Reset the DB to empty | `alembic downgrade base` |
| Preview migration SQL without running it | `alembic upgrade head --sql` |
| Run tests | `pytest` |

### Verify the schema matches the reference DDL

`schema.sql` is the reviewed reference design. This check builds a throwaway database from it
and diffs its schema against the one Alembic created. If the diff is empty, they match.

```bash
export PGHOST=localhost PGUSER=postgres PGPASSWORD='<your password>'
createdb rewind_ddl_check
psql -q -v ON_ERROR_STOP=1 -d rewind_ddl_check -f /path/to/schema.sql

dump() { pg_dump --schema-only --no-owner --no-privileges -T alembic_version "$1" \
         | grep -v '^--' | grep -v '^\\\(un\)\?restrict' | sed '/^$/d'; }
diff <(dump rewind_ddl_check) <(dump rewind) && echo "IDENTICAL"

dropdb rewind_ddl_check
```

## Project layout (DB layer)

```
backend/
├── .env / .env.example      # DATABASE_URL (.env is gitignored)
├── requirements.txt
├── alembic.ini              # sqlalchemy.url intentionally unset
├── alembic/
│   ├── env.py               # reads DATABASE_URL from app.core.config; target_metadata = Base.metadata
│   └── versions/            # migrations (initial: 6e60dd9daf95_initial_schema.py)
└── app/
    ├── core/config.py       # pydantic-settings `Settings`, loads .env
    ├── db/base.py           # DeclarativeBase, naming convention, CreatedAtMixin
    ├── db/session.py        # engine, SessionLocal, get_db() FastAPI dependency
    └── models/
        ├── user.py            # User
        ├── batch.py           # Batch, BatchMembership, BatchRole enum
        ├── album.py           # Album, AlbumStatus enum
        ├── photo.py           # Photo, PhotoLike
        ├── story.py           # Story, StoryLike
        ├── audit_log.py       # AuditLog
        └── token_blacklist.py # TokenBlacklist
```

## Changelog

### Database layer: models and initial migration

**Dependencies** (`requirements.txt`, pinned):
- FastAPI, Uvicorn, SQLAlchemy 2.0, Alembic, psycopg 3 (`postgresql+psycopg://`), pydantic-settings, pytest, httpx.
- **PyJWT** instead of python-jose, because python-jose is effectively unmaintained.
- **bcrypt** used directly instead of passlib, because passlib is unmaintained and breaks with bcrypt ≥ 4.1.

**Settings and session**
- `app/core/config.py` holds a `Settings` class with `DATABASE_URL`, read from `.env` or the environment, plus a cached `get_settings()`.
- `app/db/session.py` sets up the engine (`pool_pre_ping=True`), `SessionLocal`, and a `get_db()` dependency that yields one session per request.

**Base and mixin** (`app/db/base.py`)
- The constraint naming convention reproduces Postgres's own default names (`users_pkey`, `users_email_key`, `albums_batch_id_fkey`, …), so the ORM, the migrations and the DDL agree.
- `CreatedAtMixin` provides `created_at TIMESTAMPTZ NOT NULL DEFAULT now()`. The default is set on the database (`server_default`), not in Python.

**Models**: all 10 tables from `schema.sql`:
- Every default is a database default, and every `ON DELETE CASCADE / SET NULL` is declared on its FK.
- Relationships over DB-cascaded FKs use `passive_deletes=True`, so Postgres performs the cascade rather than the ORM.
- Relationships over FKs without `ON DELETE` use `passive_deletes="all"`, so the database rejects the delete as designed.
- The `audit_log.metadata` column is mapped to the Python attribute `meta`, because `metadata` is reserved on declarative models.
- The month/day expression index for the "on this day" timeline is declared as a functional `Index`.

**Alembic**
- Initialised in `alembic/`. `env.py` imports `app.models` and uses `Base.metadata`, and it reads the DB URL from the app settings, not `alembic.ini`.
- `compare_type` and `compare_server_default` are enabled, so autogenerate also detects type and default changes.
- Initial migration `6e60dd9daf95`: autogenerated from the models, then hand-reviewed. The one manual edit is that `downgrade()` drops the ENUM types.

**Verified**
- A `pg_dump --schema-only` of the migrated DB is identical to one built directly from `schema.sql`.
- `alembic check` reports no drift between the models and the database.
- `downgrade base` followed by `upgrade head` round-trips cleanly.
- A smoke test confirmed the defaults, the cascades (photo → likes, album → stories → likes, photo → `pinned_photo_id` SET NULL), the CHECK and UNIQUE constraints, and the timeline index being used.

### Design decisions and known gaps

- **Hard deletes, no `deleted_at`.** Following `schema.sql`:
  - Likes, memberships, photos and stories are really deleted.
  - Users are never deleted; they are deactivated with `is_active = false`.
  - Albums are "deleted" by setting `status = 'deleted'`.
- **Album deletion does not cascade on its own.** Setting `status = 'deleted'` is an UPDATE, so the database's `ON DELETE CASCADE` never fires. The service layer must hard-delete the album's photos and stories in the same transaction.
- **`stories.pinned_photo_id` must belong to the same album as the story.** A foreign key can't express that, so the API layer has to validate it.
- **Checks left to the app layer:** batch creators must be super admins, and album reviewers must hold `batch_admin`.
