from __future__ import annotations

from dataclasses import dataclass

APP_NAME = "Italiano Trainer"
DB_FILENAME = "italiano_trainer.db"

LEVELS = ["A1", "A2", "B1", "B2"]
DIRECTIONS = ["Italiano → Русский", "Русский → Italiano", "Смешанный"]
THEMES = ["Светлая", "Тёмная"]


@dataclass(frozen=True)
class SrsDefaults:
    interval_days: int = 1
    ease_factor: float = 2.5


SRS_DEFAULTS = SrsDefaults()
