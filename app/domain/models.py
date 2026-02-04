from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Word:
    id: Optional[int]
    italian: str
    russian: str
    part_of_speech: str
    example: str
    level: str
    created_at: datetime
    updated_at: datetime
    last_review: Optional[datetime]
    next_review: Optional[datetime]
    interval_days: int
    ease_factor: float
    correct_count: int
    wrong_count: int
