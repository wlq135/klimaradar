"""Async database engine and session management."""

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    future=True,
)

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
