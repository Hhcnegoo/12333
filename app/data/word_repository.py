from __future__ import annotations

from datetime import datetime
from typing import Iterable, Optional

from app.data.database import Database
from app.domain.models import Word
from app.utils.constants import SRS_DEFAULTS


class WordRepository:
    def __init__(self, database: Database) -> None:
        self.database = database

    def add_word(
        self,
        italian: str,
        russian: str,
        part_of_speech: str,
        example: str,
        level: str,
    ) -> int:
        now = datetime.utcnow().isoformat()
        cursor = self.database.execute(
            """
            INSERT INTO words (
                italian, russian, part_of_speech, example, level,
                created_at, updated_at, last_review, next_review,
                interval_days, ease_factor, correct_count, wrong_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                italian,
                russian,
                part_of_speech,
                example,
                level,
                now,
                now,
                None,
                None,
                SRS_DEFAULTS.interval_days,
                SRS_DEFAULTS.ease_factor,
                0,
                0,
            ),
        )
        return int(cursor.lastrowid)

    def update_word(
        self,
        word_id: int,
        italian: str,
        russian: str,
        part_of_speech: str,
        example: str,
        level: str,
    ) -> None:
        now = datetime.utcnow().isoformat()
        self.database.execute(
            """
            UPDATE words
            SET italian = ?, russian = ?, part_of_speech = ?, example = ?, level = ?, updated_at = ?
            WHERE id = ?
            """,
            (italian, russian, part_of_speech, example, level, now, word_id),
        )

    def delete_word(self, word_id: int) -> None:
        self.database.execute("DELETE FROM words WHERE id = ?", (word_id,))

    def list_words(
        self,
        search: str = "",
        sort_by: str = "italian",
    ) -> list[Word]:
        query = "SELECT * FROM words"
        params: list[Iterable] = []
        if search:
            query += " WHERE italian LIKE ? OR russian LIKE ?"
            search_param = f"%{search}%"
            params.extend([search_param, search_param])
        if sort_by in {"italian", "russian", "level", "updated_at"}:
            query += f" ORDER BY {sort_by} COLLATE NOCASE"
        rows = self.database.query(query, params)
        return [self._row_to_word(row) for row in rows]

    def get_word(self, word_id: int) -> Optional[Word]:
        rows = self.database.query("SELECT * FROM words WHERE id = ?", (word_id,))
        return self._row_to_word(rows[0]) if rows else None

    def due_words(self, level: Optional[str] = None) -> list[Word]:
        now = datetime.utcnow().isoformat()
        if level:
            rows = self.database.query(
                """
                SELECT * FROM words
                WHERE (next_review IS NULL OR next_review <= ?) AND level = ?
                ORDER BY updated_at DESC
                """,
                (now, level),
            )
        else:
            rows = self.database.query(
                """
                SELECT * FROM words
                WHERE (next_review IS NULL OR next_review <= ?)
                ORDER BY updated_at DESC
                """,
                (now,),
            )
        return [self._row_to_word(row) for row in rows]

    def hardest_words(self, limit: int = 5) -> list[Word]:
        rows = self.database.query(
            """
            SELECT * FROM words
            ORDER BY wrong_count DESC, correct_count ASC
            LIMIT ?
            """,
            (limit,),
        )
        return [self._row_to_word(row) for row in rows]

    def stats(self) -> dict[str, int]:
        total = self.database.query("SELECT COUNT(*) as count FROM words")[0]["count"]
        due = self.database.query(
            "SELECT COUNT(*) as count FROM words WHERE next_review IS NULL OR next_review <= ?",
            (datetime.utcnow().isoformat(),),
        )[0]["count"]
        mastered = self.database.query(
            "SELECT COUNT(*) as count FROM words WHERE correct_count >= 5 AND wrong_count = 0"
        )[0]["count"]
        return {"total": total, "due": due, "mastered": mastered}

    def update_review(
        self,
        word_id: int,
        last_review: datetime,
        next_review: datetime,
        interval_days: int,
        ease_factor: float,
        correct: bool,
    ) -> None:
        if correct:
            self.database.execute(
                """
                UPDATE words
                SET last_review = ?, next_review = ?, interval_days = ?, ease_factor = ?,
                    correct_count = correct_count + 1, updated_at = ?
                WHERE id = ?
                """,
                (
                    last_review.isoformat(),
                    next_review.isoformat(),
                    interval_days,
                    ease_factor,
                    last_review.isoformat(),
                    word_id,
                ),
            )
        else:
            self.database.execute(
                """
                UPDATE words
                SET last_review = ?, next_review = ?, interval_days = ?, ease_factor = ?,
                    wrong_count = wrong_count + 1, updated_at = ?
                WHERE id = ?
                """,
                (
                    last_review.isoformat(),
                    next_review.isoformat(),
                    interval_days,
                    ease_factor,
                    last_review.isoformat(),
                    word_id,
                ),
            )

    def _row_to_word(self, row) -> Word:
        return Word(
            id=row["id"],
            italian=row["italian"],
            russian=row["russian"],
            part_of_speech=row["part_of_speech"],
            example=row["example"],
            level=row["level"],
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
            last_review=datetime.fromisoformat(row["last_review"])
            if row["last_review"]
            else None,
            next_review=datetime.fromisoformat(row["next_review"])
            if row["next_review"]
            else None,
            interval_days=row["interval_days"],
            ease_factor=row["ease_factor"],
            correct_count=row["correct_count"],
            wrong_count=row["wrong_count"],
        )
