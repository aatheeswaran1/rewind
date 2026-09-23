# Rewind

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![GitHub](https://img.shields.io/badge/GitHub-aatheeswaran1/rewind-blue)](https://github.com/aatheeswaran1/rewind)

A shared photo platform for college classmates with a nostalgia timeline.

## Features
- Browse classmate photos by year
- Timeline view of memories
- Search and filter functionality

## Tech Stack
- **Frontend**: React, Tailwind CSS (coming soon)
- **Backend**: Python, FastAPI, SQLAlchemy 2.x, Alembic
- **Database**: PostgreSQL

## Installation

### Backend
See [backend/README.md](backend/README.md) for setup, everyday commands (migrations, schema checks) and the changelog.

Quick start (from `backend/`):
```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then set your DATABASE_URL
alembic upgrade head
```

### Frontend
Coming soon...

## License
MIT
