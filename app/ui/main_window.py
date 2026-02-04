from __future__ import annotations

from dataclasses import dataclass
import random
from typing import Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from app.data.word_repository import WordRepository
from app.domain.models import Word
from app.services.training_service import TrainingItem, TrainingService
from app.services.tts_service import TtsService
from app.ui.theme import apply_dark_theme, apply_light_theme
from app.utils.constants import DIRECTIONS, LEVELS, THEMES


@dataclass
class QuickTestState:
    queue: list[TrainingItem]
    total: int
    correct: int = 0


class MainWindow(QMainWindow):
    def __init__(
        self,
        app: QApplication,
        repository: WordRepository,
        training_service: TrainingService,
        tts_service: TtsService,
    ) -> None:
        super().__init__()
        self.app = app
        self.repository = repository
        self.training_service = training_service
        self.tts_service = tts_service
        self.current_word_id: Optional[int] = None
        self.current_training_item: Optional[TrainingItem] = None
        self.quick_test: Optional[QuickTestState] = None

        self.setWindowTitle("Italiano Trainer")
        self.setMinimumSize(1100, 720)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.dictionary_tab = QWidget()
        self.training_tab = QWidget()
        self.stats_tab = QWidget()
        self.settings_tab = QWidget()

        self.tabs.addTab(self.dictionary_tab, "Словарь")
        self.tabs.addTab(self.training_tab, "Тренировка")
        self.tabs.addTab(self.stats_tab, "Статистика")
        self.tabs.addTab(self.settings_tab, "Настройки")

        self._build_dictionary_tab()
        self._build_training_tab()
        self._build_stats_tab()
        self._build_settings_tab()

        self.refresh_dictionary()
        self.refresh_stats()

    def _build_dictionary_tab(self) -> None:
        layout = QVBoxLayout()
        form_group = QGroupBox("Добавление и редактирование")
        form_layout = QFormLayout()
        self.italian_input = QLineEdit()
        self.russian_input = QLineEdit()
        self.pos_input = QLineEdit()
        self.example_input = QTextEdit()
        self.example_input.setFixedHeight(80)
        self.level_input = QComboBox()
        self.level_input.addItems(LEVELS)
        form_layout.addRow("Italiano", self.italian_input)
        form_layout.addRow("Русский", self.russian_input)
        form_layout.addRow("Часть речи", self.pos_input)
        form_layout.addRow("Пример", self.example_input)
        form_layout.addRow("Уровень", self.level_input)
        form_group.setLayout(form_layout)

        actions_layout = QGridLayout()
        self.add_button = QPushButton("Добавить")
        self.update_button = QPushButton("Сохранить")
        self.delete_button = QPushButton("Удалить")
        self.clear_button = QPushButton("Очистить")
        actions_layout.addWidget(self.add_button, 0, 0)
        actions_layout.addWidget(self.update_button, 0, 1)
        actions_layout.addWidget(self.delete_button, 0, 2)
        actions_layout.addWidget(self.clear_button, 0, 3)

        filter_layout = QGridLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Поиск по словам…")
        self.sort_input = QComboBox()
        self.sort_input.addItems(["italian", "russian", "level", "updated_at"])
        filter_layout.addWidget(QLabel("Поиск"), 0, 0)
        filter_layout.addWidget(self.search_input, 0, 1)
        filter_layout.addWidget(QLabel("Сортировка"), 0, 2)
        filter_layout.addWidget(self.sort_input, 0, 3)

        self.words_table = QTableWidget(0, 9)
        self.words_table.setHorizontalHeaderLabels(
            [
                "ID",
                "Italiano",
                "Русский",
                "Часть речи",
                "Пример",
                "Уровень",
                "Correct",
                "Wrong",
                "Next",
            ]
        )
        self.words_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.words_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.words_table.setColumnHidden(0, True)
        self.words_table.horizontalHeader().setStretchLastSection(True)

        layout.addWidget(form_group)
        layout.addLayout(actions_layout)
        layout.addLayout(filter_layout)
        layout.addWidget(self.words_table)

        self.dictionary_tab.setLayout(layout)

        self.add_button.clicked.connect(self.add_word)
        self.update_button.clicked.connect(self.update_word)
        self.delete_button.clicked.connect(self.delete_word)
        self.clear_button.clicked.connect(self.clear_form)
        self.search_input.textChanged.connect(self.refresh_dictionary)
        self.sort_input.currentTextChanged.connect(self.refresh_dictionary)
        self.words_table.itemSelectionChanged.connect(self.load_selected_word)

    def _build_training_tab(self) -> None:
        layout = QVBoxLayout()
        options_group = QGroupBox("Параметры тренировки")
        options_layout = QGridLayout()
        self.direction_input = QComboBox()
        self.direction_input.addItems(DIRECTIONS)
        self.level_filter = QComboBox()
        self.level_filter.addItem("Все уровни")
        self.level_filter.addItems(LEVELS)
        self.quick_count = QSpinBox()
        self.quick_count.setRange(5, 10)
        self.quick_count.setValue(5)
        self.quick_start_button = QPushButton("Быстрый тест")

        options_layout.addWidget(QLabel("Направление"), 0, 0)
        options_layout.addWidget(self.direction_input, 0, 1)
        options_layout.addWidget(QLabel("Уровень"), 0, 2)
        options_layout.addWidget(self.level_filter, 0, 3)
        options_layout.addWidget(QLabel("Количество"), 0, 4)
        options_layout.addWidget(self.quick_count, 0, 5)
        options_layout.addWidget(self.quick_start_button, 0, 6)
        options_group.setLayout(options_layout)

        training_group = QGroupBox("Слово")
        training_layout = QVBoxLayout()
        self.word_label = QLabel("Нажмите 'Следующее' для начала")
        self.word_label.setAlignment(Qt.AlignCenter)
        self.word_label.setStyleSheet("font-size: 28px; font-weight: 600;")
        self.direction_label = QLabel("")
        self.direction_label.setAlignment(Qt.AlignCenter)
        self.answer_input = QLineEdit()
        self.answer_input.setPlaceholderText("Введите перевод…")
        self.feedback_label = QLabel("")
        self.feedback_label.setAlignment(Qt.AlignCenter)
        self.feedback_label.setStyleSheet("font-size: 16px;")
        training_layout.addWidget(self.word_label)
        training_layout.addWidget(self.direction_label)
        training_layout.addWidget(self.answer_input)
        training_layout.addWidget(self.feedback_label)
        training_group.setLayout(training_layout)

        buttons_layout = QGridLayout()
        self.check_button = QPushButton("Проверить")
        self.next_button = QPushButton("Следующее")
        self.speak_button = QPushButton("Озвучить")
        buttons_layout.addWidget(self.check_button, 0, 0)
        buttons_layout.addWidget(self.next_button, 0, 1)
        buttons_layout.addWidget(self.speak_button, 0, 2)

        layout.addWidget(options_group)
        layout.addWidget(training_group)
        layout.addLayout(buttons_layout)
        layout.addStretch()

        self.training_tab.setLayout(layout)

        self.next_button.clicked.connect(self.next_training_item)
        self.check_button.clicked.connect(self.check_training_answer)
        self.quick_start_button.clicked.connect(self.start_quick_test)
        self.speak_button.clicked.connect(self.speak_current_word)

    def _build_stats_tab(self) -> None:
        layout = QVBoxLayout()
        self.total_label = QLabel()
        self.due_label = QLabel()
        self.mastered_label = QLabel()
        self.hard_table = QTableWidget(0, 4)
        self.hard_table.setHorizontalHeaderLabels(["Italiano", "Русский", "Wrong", "Correct"])
        self.hard_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.hard_table.setSelectionBehavior(QAbstractItemView.SelectRows)

        layout.addWidget(QLabel("Общий прогресс"))
        layout.addWidget(self.total_label)
        layout.addWidget(self.due_label)
        layout.addWidget(self.mastered_label)
        layout.addWidget(QLabel("Сложные слова"))
        layout.addWidget(self.hard_table)
        self.stats_tab.setLayout(layout)

    def _build_settings_tab(self) -> None:
        layout = QVBoxLayout()
        theme_group = QGroupBox("Тема")
        theme_layout = QFormLayout()
        self.theme_input = QComboBox()
        self.theme_input.addItems(THEMES)
        theme_layout.addRow("Выбор", self.theme_input)
        theme_group.setLayout(theme_layout)

        layout.addWidget(theme_group)
        layout.addStretch()
        self.settings_tab.setLayout(layout)

        self.theme_input.currentTextChanged.connect(self.apply_theme)

    def apply_theme(self, theme: str) -> None:
        if theme == "Тёмная":
            apply_dark_theme(self.app)
        else:
            apply_light_theme(self.app)

    def refresh_dictionary(self) -> None:
        search = self.search_input.text().strip()
        sort_by = self.sort_input.currentText()
        words = self.repository.list_words(search=search, sort_by=sort_by)
        self.words_table.setRowCount(len(words))
        for row_index, word in enumerate(words):
            self.words_table.setItem(row_index, 0, QTableWidgetItem(str(word.id)))
            self.words_table.setItem(row_index, 1, QTableWidgetItem(word.italian))
            self.words_table.setItem(row_index, 2, QTableWidgetItem(word.russian))
            self.words_table.setItem(row_index, 3, QTableWidgetItem(word.part_of_speech))
            self.words_table.setItem(row_index, 4, QTableWidgetItem(word.example))
            self.words_table.setItem(row_index, 5, QTableWidgetItem(word.level))
            self.words_table.setItem(row_index, 6, QTableWidgetItem(str(word.correct_count)))
            self.words_table.setItem(row_index, 7, QTableWidgetItem(str(word.wrong_count)))
            next_review = word.next_review.isoformat() if word.next_review else "—"
            self.words_table.setItem(row_index, 8, QTableWidgetItem(next_review))
        self.words_table.resizeColumnsToContents()
        self.refresh_stats()

    def load_selected_word(self) -> None:
        selected = self.words_table.selectedItems()
        if not selected:
            return
        word_id = int(selected[0].text())
        word = self.repository.get_word(word_id)
        if not word:
            return
        self.current_word_id = word.id
        self.italian_input.setText(word.italian)
        self.russian_input.setText(word.russian)
        self.pos_input.setText(word.part_of_speech)
        self.example_input.setPlainText(word.example)
        self.level_input.setCurrentText(word.level)

    def clear_form(self) -> None:
        self.current_word_id = None
        self.italian_input.clear()
        self.russian_input.clear()
        self.pos_input.clear()
        self.example_input.clear()
        self.level_input.setCurrentIndex(0)
        self.words_table.clearSelection()

    def add_word(self) -> None:
        italian = self.italian_input.text().strip()
        russian = self.russian_input.text().strip()
        part_of_speech = self.pos_input.text().strip()
        example = self.example_input.toPlainText().strip()
        level = self.level_input.currentText()
        if not italian or not russian or not part_of_speech or not example:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
            return
        self.repository.add_word(italian, russian, part_of_speech, example, level)
        self.clear_form()
        self.refresh_dictionary()

    def update_word(self) -> None:
        if self.current_word_id is None:
            QMessageBox.information(self, "Выбор", "Выберите слово для редактирования.")
            return
        italian = self.italian_input.text().strip()
        russian = self.russian_input.text().strip()
        part_of_speech = self.pos_input.text().strip()
        example = self.example_input.toPlainText().strip()
        level = self.level_input.currentText()
        if not italian or not russian or not part_of_speech or not example:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля.")
            return
        self.repository.update_word(
            self.current_word_id,
            italian,
            russian,
            part_of_speech,
            example,
            level,
        )
        self.refresh_dictionary()

    def delete_word(self) -> None:
        if self.current_word_id is None:
            QMessageBox.information(self, "Выбор", "Выберите слово для удаления.")
            return
        confirmed = QMessageBox.question(
            self,
            "Удаление",
            "Удалить выбранное слово?",
        )
        if confirmed == QMessageBox.Yes:
            self.repository.delete_word(self.current_word_id)
            self.clear_form()
            self.refresh_dictionary()

    def next_training_item(self) -> None:
        if self.quick_test and self.quick_test.queue:
            item = self.quick_test.queue.pop(0)
            self.set_training_item(item)
            return
        level = self._selected_level()
        item = self.training_service.get_training_item(level, self.direction_input.currentText())
        if not item:
            self.word_label.setText("Нет слов для повторения")
            self.direction_label.setText("")
            self.current_training_item = None
            return
        self.set_training_item(item)

    def set_training_item(self, item: TrainingItem) -> None:
        self.current_training_item = item
        if item.direction == "Italiano → Русский":
            self.word_label.setText(item.word.italian)
        else:
            self.word_label.setText(item.word.russian)
        self.direction_label.setText(item.direction)
        self.answer_input.clear()
        self.feedback_label.setText("")

    def check_training_answer(self) -> None:
        if not self.current_training_item:
            return
        answer = self.answer_input.text().strip()
        if not answer:
            QMessageBox.information(self, "Ответ", "Введите ответ.")
            return
        correct = self.training_service.check_answer(self.current_training_item, answer)
        if correct:
            self.feedback_label.setStyleSheet("color: #2e7d32; font-size: 16px;")
            self.feedback_label.setText("Верно! Отличная работа.")
        else:
            expected = (
                self.current_training_item.word.russian
                if self.current_training_item.direction == "Italiano → Русский"
                else self.current_training_item.word.italian
            )
            self.feedback_label.setStyleSheet("color: #c62828; font-size: 16px;")
            self.feedback_label.setText(f"Неверно. Правильный ответ: {expected}")
        self.training_service.register_result(self.current_training_item, correct)
        if self.quick_test:
            if correct:
                self.quick_test.correct += 1
            if not self.quick_test.queue:
                QMessageBox.information(
                    self,
                    "Тест завершён",
                    f"Результат: {self.quick_test.correct}/{self.quick_test.total}",
                )
                self.quick_test = None
        self.refresh_dictionary()

    def start_quick_test(self) -> None:
        level = self._selected_level()
        direction = self.direction_input.currentText()
        words = self.repository.due_words(level=level)
        if not words:
            QMessageBox.information(self, "Тест", "Нет слов для теста.")
            return
        count = min(self.quick_count.value(), len(words))
        sample = random.sample(words, count)
        items = [
            TrainingItem(word=word, direction=self._resolve_direction(direction))
            for word in sample
        ]
        self.quick_test = QuickTestState(queue=items, total=count)
        self.next_training_item()

    def speak_current_word(self) -> None:
        if not self.current_training_item:
            return
        self.tts_service.speak(self.current_training_item.word.italian)

    def refresh_stats(self) -> None:
        stats = self.repository.stats()
        self.total_label.setText(f"Всего слов: {stats['total']}")
        self.due_label.setText(f"К повторению: {stats['due']}")
        self.mastered_label.setText(f"Освоено: {stats['mastered']}")
        hardest = self.repository.hardest_words()
        self.hard_table.setRowCount(len(hardest))
        for row_index, word in enumerate(hardest):
            self.hard_table.setItem(row_index, 0, QTableWidgetItem(word.italian))
            self.hard_table.setItem(row_index, 1, QTableWidgetItem(word.russian))
            self.hard_table.setItem(row_index, 2, QTableWidgetItem(str(word.wrong_count)))
            self.hard_table.setItem(row_index, 3, QTableWidgetItem(str(word.correct_count)))
        self.hard_table.resizeColumnsToContents()

    def _selected_level(self) -> Optional[str]:
        level_text = self.level_filter.currentText()
        return None if level_text == "Все уровни" else level_text

    @staticmethod
    def _resolve_direction(direction: str) -> str:
        if direction == "Смешанный":
            return random.choice(["Italiano → Русский", "Русский → Italiano"])
        return direction
