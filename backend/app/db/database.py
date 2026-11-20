import sqlite3
import json
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator

from app.core.config import settings


def initialize_database() -> None:
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    with connection() as db:
        db.executescript("""
        CREATE TABLE IF NOT EXISTS assignments (
            id TEXT PRIMARY KEY, title TEXT NOT NULL, description TEXT NOT NULL DEFAULT '',
            course TEXT NOT NULL DEFAULT '', due_date TEXT, status TEXT NOT NULL DEFAULT 'Not started',
            created_at TEXT NOT NULL, attachment_names TEXT NOT NULL DEFAULT '[]', extracted_text TEXT NOT NULL DEFAULT ''
        );
        CREATE TABLE IF NOT EXISTS memories (
            id TEXT PRIMARY KEY, content TEXT NOT NULL, category TEXT NOT NULL DEFAULT 'general',
            created_at TEXT NOT NULL, updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_assignments_created_at ON assignments(created_at DESC);
        CREATE INDEX IF NOT EXISTS idx_memories_updated_at ON memories(updated_at DESC);
        """)
        legacy_store = settings.database_path.parent / "assignments.json"
        existing = db.execute("SELECT COUNT(*) FROM assignments").fetchone()[0]
        if existing == 0 and legacy_store.exists():
            try:
                rows = json.loads(legacy_store.read_text(encoding="utf-8"))
                for item in rows:
                    db.execute("""INSERT OR IGNORE INTO assignments
                        (id,title,description,course,due_date,status,created_at,attachment_names,extracted_text)
                        VALUES(?,?,?,?,?,?,?,?,?)""", (
                        item["id"], item["title"], item.get("description", ""), item.get("course", ""),
                        item.get("due_date"), item.get("status", "Not started"), item["created_at"],
                        json.dumps(item.get("attachment_names", []), ensure_ascii=False), item.get("extracted_text", "")))
            except (OSError, ValueError, KeyError, TypeError):
                # Keep the legacy file intact if it is malformed; new writes use SQLite.
                pass


@contextmanager
def connection() -> Iterator[sqlite3.Connection]:
    db = sqlite3.connect(Path(settings.database_path), timeout=10)
    db.row_factory = sqlite3.Row
    db.execute("PRAGMA foreign_keys = ON")
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
