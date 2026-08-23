"""Tests for lightweight SQLite schema migrations."""

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

import app.database as database


@pytest.mark.asyncio
async def test_run_migrations_adds_click_and_subscription_attribution(tmp_path, monkeypatch):
    db_path = tmp_path / "migration.db"
    engine = create_async_engine(f"sqlite+aiosqlite:///{db_path.as_posix()}")
    monkeypatch.setattr(database, "engine", engine)

    async with engine.begin() as conn:
        await conn.execute(
            text(
                """
                CREATE TABLE alert_subscriptions (
                    id INTEGER PRIMARY KEY,
                    email VARCHAR(255) NOT NULL,
                    country VARCHAR(2) NOT NULL
                )
                """
            )
        )
        await conn.execute(
            text(
                """
                CREATE TABLE click_events (
                    id INTEGER PRIMARY KEY,
                    listing_id INTEGER NOT NULL,
                    clicked_at DATETIME NOT NULL,
                    source VARCHAR(50),
                    user_agent TEXT,
                    ip_hash VARCHAR(64)
                )
                """
            )
        )

    await database.run_migrations()

    async with engine.connect() as conn:
        alert_columns = {
            row[1] for row in (await conn.execute(text("PRAGMA table_info(alert_subscriptions)"))).fetchall()
        }
        click_columns = {
            row[1] for row in (await conn.execute(text("PRAGMA table_info(click_events)"))).fetchall()
        }
        indexes = {
            row[1]
            for row in (
                await conn.execute(text("PRAGMA index_list(click_events)"))
            ).fetchall()
        }

    assert {"frequency", "digest_last_sent_at", "source"} <= alert_columns
    assert {"placement", "position", "page_ref"} <= click_columns
    assert "ix_click_events_placement" in indexes

    await engine.dispose()
