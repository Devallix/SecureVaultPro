"""SQLAlchemy engine factory for SecureVault Pro."""

from typing import Any

from sqlalchemy import event
from sqlalchemy.engine import Engine

from app.core.config import AppConfig
from app.logging.logger import get_logger

logger = get_logger(__name__)


def create_engine(config: AppConfig | None = None) -> Engine:
    """Create and configure the SQLAlchemy engine.

    Enables WAL mode, foreign keys, and busy timeout for SQLite.

    Args:
        config: Application configuration. Uses default if None.

    Returns:
        Configured SQLAlchemy Engine instance.
    """
    if config is None:
        config = AppConfig()

    from sqlalchemy import create_engine as sa_create_engine

    db_url = config.database_url
    logger.info("Creating database engine: {url}", url=db_url.split("?")[0])

    engine = sa_create_engine(
        db_url,
        echo=False,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection: Any, connection_record: Any) -> None:
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA journal_mode=WAL")
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.execute("PRAGMA busy_timeout=5000")
        cursor.execute("PRAGMA synchronous=NORMAL")
        cursor.close()

    return engine
