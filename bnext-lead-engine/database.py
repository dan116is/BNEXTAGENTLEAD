"""
Bnext Lead Engine — SQLite database layer with hard deduplication on (name, city).
"""

import sqlite3
import logging
from contextlib import contextmanager

import config

logger = logging.getLogger("db")


def init_db(path: str = config.DB_PATH) -> None:
    with _conn(path) as db:
        db.executescript("""
            CREATE TABLE IF NOT EXISTS leads (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                name        TEXT    NOT NULL,
                city        TEXT    NOT NULL,
                segment     TEXT,
                phone       TEXT,
                website     TEXT,
                rating      REAL,
                lat         REAL,
                lng         REAL,
                region      TEXT,
                agent       TEXT,
                channel     TEXT,
                sales_angle TEXT,
                categories  TEXT,
                status      TEXT    DEFAULT 'discovered',
                created_at  DATETIME DEFAULT (datetime('now')),
                UNIQUE(name, city)
            );

            CREATE TABLE IF NOT EXISTS run_log (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                run_at      DATETIME DEFAULT (datetime('now')),
                discovered  INTEGER DEFAULT 0,
                enriched    INTEGER DEFAULT 0,
                routed      INTEGER DEFAULT 0,
                errors      TEXT
            );
        """)


@contextmanager
def _conn(path: str = config.DB_PATH):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def insert_lead(lead: dict, path: str = config.DB_PATH) -> bool:
    """Insert a lead; silently skip duplicates. Returns True if inserted."""
    try:
        with _conn(path) as db:
            db.execute(
                """INSERT OR IGNORE INTO leads (name, city, segment, lat, lng, region)
                   VALUES (:name, :city, :segment, :lat, :lng, :region)""",
                lead,
            )
            if db.execute(
                "SELECT changes() AS c"
            ).fetchone()["c"]:
                return True
        return False
    except Exception as e:
        logger.error("insert_lead failed for %s / %s: %s", lead.get("name"), lead.get("city"), e)
        return False


def get_leads_by_status(status: str, path: str = config.DB_PATH) -> list[dict]:
    with _conn(path) as db:
        rows = db.execute(
            "SELECT * FROM leads WHERE status = ?", (status,)
        ).fetchall()
    return [dict(r) for r in rows]


def update_lead(lead_id: int, updates: dict, path: str = config.DB_PATH) -> None:
    if not updates:
        return
    cols = ", ".join(f"{k} = :{k}" for k in updates)
    updates["id"] = lead_id
    with _conn(path) as db:
        db.execute(f"UPDATE leads SET {cols} WHERE id = :id", updates)


def count_leads(path: str = config.DB_PATH) -> dict:
    with _conn(path) as db:
        total      = db.execute("SELECT COUNT(*) FROM leads").fetchone()[0]
        by_status  = db.execute(
            "SELECT status, COUNT(*) FROM leads GROUP BY status"
        ).fetchall()
        by_segment = db.execute(
            "SELECT segment, COUNT(*) FROM leads GROUP BY segment"
        ).fetchall()
        by_region  = db.execute(
            "SELECT region, COUNT(*) FROM leads GROUP BY region"
        ).fetchall()
        by_channel = db.execute(
            "SELECT channel, COUNT(*) FROM leads WHERE channel IS NOT NULL GROUP BY channel"
        ).fetchall()
    return {
        "total": total,
        "by_status":  {r[0]: r[1] for r in by_status},
        "by_segment": {r[0]: r[1] for r in by_segment},
        "by_region":  {r[0]: r[1] for r in by_region},
        "by_channel": {r[0]: r[1] for r in by_channel},
    }


def log_run(stats: dict, path: str = config.DB_PATH) -> None:
    with _conn(path) as db:
        db.execute(
            """INSERT INTO run_log (discovered, enriched, routed, errors)
               VALUES (:discovered, :enriched, :routed, :errors)""",
            stats,
        )
