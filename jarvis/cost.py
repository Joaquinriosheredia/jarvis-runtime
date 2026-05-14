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
        CREATE TABLE IF NOT EXISTS usage (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp  TEXT  NOT NULL,
            source     TEXT  NOT NULL,
            tokens     INTEGER NOT NULL DEFAULT 0,
            cost_usd   REAL    NOT NULL DEFAULT 0
        )
    """)
    conn.commit()


def record_usage(source: str, tokens: int, cost_usd: float) -> None:
    try:
        with _connect() as conn:
            _init_db(conn)
            conn.execute(
                "INSERT INTO usage (timestamp, source, tokens, cost_usd) VALUES (?, ?, ?, ?)",
                (datetime.utcnow().isoformat(), source, tokens, cost_usd),
            )
    except Exception as e:
        logger.warning(f"No se pudo registrar uso: {e}")


def get_usage_summary() -> dict[str, Any]:
    try:
        with _connect() as conn:
            _init_db(conn)
            rows = conn.execute("SELECT source, SUM(tokens) as tokens, SUM(cost_usd) as cost FROM usage GROUP BY source").fetchall()
            total_tokens = conn.execute("SELECT SUM(tokens) FROM usage").fetchone()[0] or 0
            total_cost = conn.execute("SELECT SUM(cost_usd) FROM usage").fetchone()[0] or 0.0
            total_requests = conn.execute("SELECT COUNT(*) FROM usage").fetchone()[0] or 0

            by_source = {r["source"]: {"tokens": r["tokens"], "cost_usd": round(r["cost"], 6)} for r in rows}

            return {
                "total_requests": total_requests,
                "total_tokens": total_tokens,
                "total_cost_usd": round(total_cost, 6),
                "by_source": by_source,
            }
    except Exception as e:
        logger.warning(f"No se pudo obtener resumen de uso: {e}")
        return {"total_requests": 0, "total_tokens": 0, "total_cost_usd": 0.0, "by_source": {}}
