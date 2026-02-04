from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class SrsResult:
    next_review: datetime
    interval_days: int
    ease_factor: float


class SrsService:
    def calculate(self, interval_days: int, ease_factor: float, correct: bool) -> SrsResult:
        if correct:
            new_interval = max(1, int(interval_days * ease_factor))
            new_ease = min(2.8, ease_factor + 0.1)
        else:
            new_interval = 1
            new_ease = max(1.3, ease_factor - 0.2)
        next_review = datetime.utcnow() + timedelta(days=new_interval)
        return SrsResult(next_review=next_review, interval_days=new_interval, ease_factor=new_ease)
