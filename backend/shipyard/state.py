"""Mutable per-item loop state. The only thing that changes at runtime.

One SQLite file, one table. Rows exist only for items the user has touched.
"""
from __future__ import annotations

import sqlite3
from datetime import date, datetime, timezone
from pathlib import Path

from .config import settings

_SCHEMA = """
CREATE TABLE IF NOT EXISTS item_state (
    item_id      TEXT PRIMARY KEY,
    user_note    TEXT,
    user_intent  TEXT,
    scheduled_at TEXT,
    status       TEXT NOT NULL DEFAULT 'saved',
    resolved_at  TEXT,
    updated_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS ix_state_status ON item_state(status);
CREATE INDEX IF NOT EXISTS ix_state_sched  ON item_state(scheduled_at);

CREATE TABLE IF NOT EXISTS promoted (
    item_id    TEXT PRIMARY KEY,       -- liked items promoted into the saved loop
    created_at TEXT NOT NULL
);
"""


def _conn() -> sqlite3.Connection:
    Path(settings.db_path).parent.mkdir(parents=True, exist_ok=True)
    c = sqlite3.connect(settings.db_path)
    c.row_factory = sqlite3.Row
    c.execute("PRAGMA journal_mode=WAL")
    return c


def init_db() -> None:
    with _conn() as c:
        c.executescript(_SCHEMA)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def get_state(item_id: str) -> dict:
    with _conn() as c:
        r = c.execute("SELECT * FROM item_state WHERE item_id=?", (item_id,)).fetchone()
    if not r:
        return {"status": "saved"}
    return {k: r[k] for k in r.keys() if k != "item_id"}


def get_states(item_ids: list[str]) -> dict[str, dict]:
    if not item_ids:
        return {}
    q = ",".join("?" * len(item_ids))
    with _conn() as c:
        rows = c.execute(
            f"SELECT * FROM item_state WHERE item_id IN ({q})", item_ids
        ).fetchall()
    return {r["item_id"]: {k: r[k] for k in r.keys() if k != "item_id"} for r in rows}


def patch_state(
    item_id: str,
    *,
    user_note: str | None = None,
    user_intent: str | None = None,
    scheduled_at: date | None = None,
    status: str | None = None,
    _unset: set[str] | None = None,
) -> dict:
    _unset = _unset or set()
    cur = get_state(item_id)
    note = None if "user_note" in _unset else (user_note if user_note is not None else cur.get("user_note"))
    intent = None if "user_intent" in _unset else (user_intent if user_intent is not None else cur.get("user_intent"))
    sched = None if "scheduled_at" in _unset else (
        scheduled_at.isoformat() if scheduled_at else cur.get("scheduled_at")
    )

    if status is None:
        status = cur.get("status", "saved")
        if status != "resolved":
            status = "scheduled" if sched else "saved"
    resolved_at = _now() if status == "resolved" else None

    with _conn() as c:
        c.execute(
            """
            INSERT INTO item_state (item_id, user_note, user_intent, scheduled_at, status, resolved_at, updated_at)
            VALUES (?,?,?,?,?,?,?)
            ON CONFLICT(item_id) DO UPDATE SET
                user_note=excluded.user_note,
                user_intent=excluded.user_intent,
                scheduled_at=excluded.scheduled_at,
                status=excluded.status,
                resolved_at=excluded.resolved_at,
                updated_at=excluded.updated_at
            """,
            (item_id, note, intent, sched, status, resolved_at, _now()),
        )
    return get_state(item_id)


def promote(item_id: str) -> None:
    with _conn() as c:
        c.execute(
            "INSERT OR IGNORE INTO promoted (item_id, created_at) VALUES (?,?)",
            (item_id, _now()),
        )


def promoted_ids() -> set[str]:
    with _conn() as c:
        return {r["item_id"] for r in c.execute("SELECT item_id FROM promoted")}


def today_ids(on: date | None = None) -> list[str]:
    """Items scheduled on/before `on` and not resolved, soonest first.

    `on` compares against dates picked in the browser's local timezone (a
    plain <input type="date">), so it must default to local "today", not
    UTC — otherwise anything scheduled for today stays invisible until UTC
    catches up, which can be most of a day off from the user's clock.
    """
    on = on or datetime.now().date()
    with _conn() as c:
        rows = c.execute(
            """
            SELECT item_id FROM item_state
            WHERE scheduled_at IS NOT NULL
              AND scheduled_at <= ?
              AND status != 'resolved'
            ORDER BY scheduled_at ASC
            """,
            (on.isoformat(),),
        ).fetchall()
    return [r["item_id"] for r in rows]


def counts() -> dict[str, int]:
    with _conn() as c:
        rows = c.execute("SELECT status, COUNT(*) n FROM item_state GROUP BY status").fetchall()
    return {r["status"]: r["n"] for r in rows}
