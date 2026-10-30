"""Thread pool manager for SecureVault Pro."""

from PySide6.QtCore import QThreadPool

_pool: QThreadPool | None = None


def get_thread_pool() -> QThreadPool:
    """Get the global thread pool instance."""
    global _pool
    if _pool is None:
        _pool = QThreadPool.globalInstance()
        if _pool is not None:
            _pool.setMaxThreadCount(4)
    return _pool


def start_worker(worker) -> None:
    """Start a worker on the global thread pool.

    Args:
        worker: A QRunnable instance to execute.
    """
    pool = get_thread_pool()
    if pool is not None:
        pool.start(worker)
