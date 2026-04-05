"""
Create PathMind database tables using SQLAlchemy metadata.

Run from the backend directory:
    python database/setup.py
"""

import asyncio
import sys
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import text


BACKEND_DIR = Path(__file__).resolve().parents[1]
ENV_FILE = BACKEND_DIR / ".env"

if ENV_FILE.exists():
    load_dotenv(ENV_FILE)
else:
    load_dotenv()

if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from models.database import Base, DATABASE_URL, engine  # noqa: E402


def get_database_name(database_url: str) -> str:
    scheme = database_url.split("://", 1)[0].lower()
    return scheme.split("+", 1)[0]


async def verify_connection() -> tuple[str, str]:
    async with engine.connect() as connection:
        result = await connection.execute(text("SELECT current_database(), current_user"))
        db_name, db_user = result.one()
    return db_name, db_user


async def create_tables() -> None:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)


async def main() -> None:
    db_backend = get_database_name(DATABASE_URL)
    print(f"[setup] DATABASE_URL backend: {db_backend}")

    if db_backend != "postgresql":
        raise RuntimeError(
            "DATABASE_URL is not PostgreSQL. Set DATABASE_URL to postgresql+asyncpg://..."
        )

    db_name, db_user = await verify_connection()
    print(f"[ok] Connected to database '{db_name}' as '{db_user}'")

    await create_tables()
    print("[ok] Database tables created/verified successfully.")

    await engine.dispose()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as exc:
        print(f"[error] {type(exc).__name__}: {exc}")
        raise
