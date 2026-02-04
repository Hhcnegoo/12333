from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable

from app.utils.constants import DB_FILENAME


class Database:
    def __init__(self, base_dir: Path) -> None:
        self.db_path = base_dir / DB_FILENAME
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row

    def initialize(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS words (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                italian TEXT NOT NULL,
                russian TEXT NOT NULL,
                part_of_speech TEXT NOT NULL,
                example TEXT NOT NULL,
                level TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                last_review TEXT,
                next_review TEXT,
                interval_days INTEGER NOT NULL,
                ease_factor REAL NOT NULL,
                correct_count INTEGER NOT NULL,
                wrong_count INTEGER NOT NULL
            );
            """
        )
        self.connection.commit()

    def execute(self, query: str, params: Iterable | None = None) -> sqlite3.Cursor:
        cursor = self.connection.execute(query, params or [])
        self.connection.commit()
        return cursor

    def query(self, query: str, params: Iterable | None = None) -> list[sqlite3.Row]:
        cursor = self.connection.execute(query, params or [])
        return cursor.fetchall()

    def close(self) -> None:
        self.connection.close()
