"""SQLite helpers for the demo application."""

from __future__ import annotations

import argparse
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from .config import get_settings


def get_connection() -> sqlite3.Connection:
    """Return a SQLite connection using the configured DB path."""
    settings = get_settings()
    db_path = settings.DB_PATH
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def _read_sql(path: Path) -> str:
    with path.open("r", encoding="utf-8") as handle:
        return handle.read()


def init_db(demo: bool = False) -> None:
    """Initialize schema and optionally load demo data."""
    base_dir = Path(__file__).resolve().parent.parent
    schema_sql = _read_sql(base_dir / "db" / "schema.sql")

    with get_connection() as conn:
        conn.executescript(schema_sql)
        if demo:
            demo_sql = _read_sql(base_dir / "db" / "demo_data.sql")
            conn.executescript(demo_sql)
        conn.commit()


def vacancy_already_applied(vacancy_id: str) -> bool:
    """Return True if the vacancy_id already exists in applications."""
    query = "SELECT 1 FROM applications WHERE vacancy_id = ? LIMIT 1"
    with get_connection() as conn:
        row = conn.execute(query, (vacancy_id,)).fetchone()
        return row is not None


def save_application(
    vacancy_id: str,
    profile_name: str,
    status: str,
    cover_letter_snippet: Optional[str],
    raw_response: Optional[str],
) -> None:
    """Persist an application attempt."""
    applied_at = datetime.now(timezone.utc).isoformat()
    query = """
        INSERT INTO applications (
            vacancy_id,
            profile_name,
            status,
            applied_at,
            cover_letter_snippet,
            raw_response
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """
    with get_connection() as conn:
        conn.execute(
            query,
            (vacancy_id, profile_name, status, applied_at, cover_letter_snippet, raw_response),
        )
        conn.commit()


def _cli() -> None:
    parser = argparse.ArgumentParser(description="Manage SQLite database for the demo.")
    parser.add_argument("--init", action="store_true", help="Create tables from schema.sql")
    parser.add_argument("--demo", action="store_true", help="Load demo data after schema init")
    args = parser.parse_args()

    if args.init and args.demo:
        init_db(demo=True)
        print("Initialized schema and loaded demo data.")
    elif args.init:
        init_db(demo=False)
        print("Initialized schema.")
    elif args.demo:
        init_db(demo=True)
        print("Initialized schema and loaded demo data.")
    else:
        parser.print_help()


if __name__ == "__main__":
    _cli()
