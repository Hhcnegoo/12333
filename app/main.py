from __future__ import annotations

import sys
from pathlib import Path

from PySide6.QtWidgets import QApplication

from app.data.database import Database
from app.data.word_repository import WordRepository
from app.services.srs_service import SrsService
from app.services.training_service import TrainingService
from app.services.tts_service import TtsService
from app.ui.main_window import MainWindow
from app.ui.theme import apply_light_theme


def main() -> int:
    app = QApplication(sys.argv)
    apply_light_theme(app)

    base_dir = Path(__file__).resolve().parent
    database = Database(base_dir)
    database.initialize()

    repository = WordRepository(database)
    training_service = TrainingService(repository, SrsService())
    tts_service = TtsService()

    window = MainWindow(app, repository, training_service, tts_service)
    window.show()

    exit_code = app.exec()
    database.close()
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
