"""
Postgres connection setup for the CSV parser cloud function.

The connection details are read from environment variables (set as runtime
environment variables on the deployed cloud function) rather than from a
`.env` file, since cloud functions don't ship with one. The engine is created
once per process and cached in `_engine`: Cloud Functions can reuse the same
running instance for several invocations ("warm starts"), so re-using one
connection pool instead of reconnecting every time is both faster and avoids
exhausting Postgres' max-connections limit under load.
"""

import logging
import os

from sqlalchemy.engine import Engine
from sqlmodel import create_engine

log = logging.getLogger(__name__)

_engine: Engine | None = None


def _build_database_url() -> str:
    """Assemble a `postgresql+psycopg://` URL from environment variables."""
    user = os.environ["POSTGRES_USER"]
    password = os.environ["POSTGRES_PASSWORD"]
    host = os.environ["POSTGRES_SERVER"]
    port = os.environ["POSTGRES_PORT"]
    db_name = os.environ["POSTGRES_DB"]
    return f"postgresql+psycopg://{user}:{password}@{host}:{port}/{db_name}"


def get_engine() -> Engine:
    """
    Return the cached SQLAlchemy engine, creating it on first use.

    Raises whatever SQLAlchemy raises if the URL is malformed or a required
    environment variable is missing. Note that a bad *connection* (wrong
    host/credentials, database unreachable) does not surface here — SQLModel
    connects lazily on the first query, not when the engine object is built.
    """
    global _engine
    if _engine is None:
        _engine = create_engine(_build_database_url())
    return _engine


def check_connection() -> None:
    """
    Actively verify the database is reachable, raising `SQLAlchemyError` if not.

    Called once at the start of processing so a connection problem is caught
    immediately with a clear error, instead of surfacing later as a confusing
    failure in the middle of an unrelated query.
    """
    with get_engine().connect() as connection:
        connection.exec_driver_sql("SELECT 1")
