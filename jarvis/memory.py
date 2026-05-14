import sqlite3
import logging
from datetime import datetime
from typing import Any

from jarvis.config import DB_PATH

logger = logging.getLogger(__name__)


def _connect() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db(conn: sqlite3.Connection) -> None:
    conn.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT    NOT NULL,
            prompt    TEXT    NOT NULL,
            response  TEXT    NOT NULL,
            source    TEXT    NOT NULL,
            latency   REAL    NOT NULL DEFAULT 0,
            cost      REAL    NOT NULL DEFAULT 0
        )
    """)
    conn.commit()


def save_memory(
    prompt: str,
    response: str,
    source: str,
    latency: float = 0.0,
    cost: float = 0.0,
) -> None:
    try:
        with _connect() as conn:
            _init_db(conn)
            conn.execute(
                """INSERT INTO memories (timestamp, prompt, response, source, latency, cost)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (datetime.utcnow().isoformat(), prompt, response, source, latency, cost),
            )
    except Exception as e:
        logger.warning(f"No se pudo guardar memoria: {e}")


def get_recent_memories(limit: int = 10) -> list[dict[str, Any]]:
    try:
        with _connect() as conn:
            _init_db(conn)
            rows = conn.execute(
                "SELECT * FROM memories ORDER BY id DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]
    except Exception as e:
        logger.warning(f"No se pudo leer memoria: {e}")
        return []
