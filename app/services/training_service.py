from __future__ import annotations

import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from app.data.word_repository import WordRepository
from app.domain.models import Word
from app.services.srs_service import SrsService


@dataclass
class TrainingItem:
    word: Word
    direction: str


class TrainingService:
    def __init__(self, repository: WordRepository, srs_service: SrsService) -> None:
        self.repository = repository
        self.srs_service = srs_service

    def get_training_item(self, level: Optional[str], direction: str) -> Optional[TrainingItem]:
        pool = self.repository.due_words(level=level)
        if not pool:
            return None
        word = random.choice(pool)
        resolved_direction = direction
        if direction == "Смешанный":
            resolved_direction = random.choice(["Italiano → Русский", "Русский → Italiano"])
        return TrainingItem(word=word, direction=resolved_direction)

    def check_answer(self, item: TrainingItem, answer: str) -> bool:
        expected = item.word.russian if item.direction == "Italiano → Русский" else item.word.italian
        return answer.strip().lower() == expected.strip().lower()

    def register_result(self, item: TrainingItem, correct: bool) -> None:
        now = datetime.utcnow()
        srs = self.srs_service.calculate(
            interval_days=item.word.interval_days,
            ease_factor=item.word.ease_factor,
            correct=correct,
        )
        self.repository.update_review(
            word_id=item.word.id,
            last_review=now,
            next_review=srs.next_review,
            interval_days=srs.interval_days,
            ease_factor=srs.ease_factor,
            correct=correct,
        )
