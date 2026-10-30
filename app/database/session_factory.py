"""Database session factory for SecureVault Pro."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy.orm import Session, sessionmaker

from app.core.config import AppConfig
from app.database.engine import create_engine
from app.logging.logger import get_logger

logger = get_logger(__name__)

_session_factory: sessionmaker | None = None
_engine = None


def init_session_factory(config: AppConfig | None = None) -> sessionmaker:
    """Initialize the global session factory.

    Args:
        config: Application configuration. Uses default if None.

    Returns:
        The configured sessionmaker instance.
    """
    global _session_factory, _engine
    _engine = create_engine(config)
    _session_factory = sessionmaker(bind=_engine, expire_on_commit=False)
    logger.info("Session factory initialized")
    return _session_factory


def get_session_factory() -> sessionmaker:
    """Get the global session factory.

    Raises:
        RuntimeError: If the session factory has not been initialized.
    """
    if _session_factory is None:
        raise RuntimeError("Session factory not initialized. Call init_session_factory() first.")
    return _session_factory


@contextmanager
def get_session() -> Generator[Session]:
    """Provide a transactional database session scope.

    Automatically commits on success and rolls back on exception.

    Yields:
        SQLAlchemy Session instance.
    """
    factory = get_session_factory()
    session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def create_all_tables() -> None:
    """Create all database tables defined by ORM models."""
    import app.models  # noqa: F401 — ensure all ORM models are registered with Base.metadata
    from app.database.base import Base

    if _engine is None:
        raise RuntimeError("Engine not initialized. Call init_session_factory() first.")
    Base.metadata.create_all(_engine)
    logger.info("All database tables created")


def create_session() -> Session:
    """Create a standalone database session (non-context-manager).

    The caller is responsible for closing the session when done.

    Returns:
        SQLAlchemy Session instance.
    """
    factory = get_session_factory()
    return factory()


def dispose_engine() -> None:
    """Dispose the database engine connection pool."""
    if _engine is not None:
        _engine.dispose()
        logger.info("Database engine disposed")
