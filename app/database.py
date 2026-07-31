"""Async database engine and session management."""

from sqlalchemy import event, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)


@event.listens_for(engine.sync_engine, "connect")
def _set_sqlite_pragmas(dbapi_conn, connection_record):
    """Enable WAL + busy timeout on every new SQLite connection.

    Without WAL the background scraper holds an exclusive write lock that
    blocks concurrent web reads ("database is locked"). WAL lets readers
    and the single writer proceed in parallel, which is essential once the
    site serves real traffic alongside a periodic scraper. No-op for non-
    SQLite backends (e.g. PostgreSQL).
    """
    if "sqlite" not in settings.database_url:
        return
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")
    cursor.execute("PRAGMA busy_timeout=5000")
    cursor.execute("PRAGMA synchronous=NORMAL")
    cursor.execute("PRAGMA wal_autocheckpoint=1000")
    cursor.close()

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


async def get_db():
    """FastAPI dependency that yields an async database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def run_migrations() -> None:
    """Apply lightweight SQLite migrations for columns added after launch."""

    def _migrate_alert_subscriptions(sync_conn):
        result = sync_conn.execute(text("PRAGMA table_info(alert_subscriptions)"))
        columns = {row[1] for row in result}
        if "frequency" not in columns:
            sync_conn.execute(
                text(
                    "ALTER TABLE alert_subscriptions "
                    "ADD COLUMN frequency VARCHAR(20) NOT NULL DEFAULT 'immediate'"
                )
            )
        if "digest_last_sent_at" not in columns:
            sync_conn.execute(
                text(
                    "ALTER TABLE alert_subscriptions "
                    "ADD COLUMN digest_last_sent_at DATETIME"
                )
            )

    async with engine.begin() as conn:
        await conn.run_sync(_migrate_alert_subscriptions)
