# Italiano Trainer

Минималистичное десктопное приложение для изучения итальянского языка с активной практикой и интервальными повторениями.

## Возможности

- словарь с добавлением, редактированием, удалением слов и примером
- поиск и сортировка
- тренировки: Italiano → Русский / Русский → Italiano / смешанный режим
- визуальная обратная связь и показ правильного ответа
- интервальные повторения (SRS)
- статистика прогресса и список сложных слов
- быстрый тест на 5–10 слов
- озвучка итальянских слов
- светлая и тёмная темы

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -m app.main
```

## Архитектура

- **Domain**: модели данных (`app/domain`).
- **Data**: SQLite база и репозиторий слов (`app/data`).
- **Services**: логика тренировок, SRS и TTS (`app/services`).
- **UI**: PySide6 интерфейс (`app/ui`).

## Структура проекта

```
app/
  data/
    database.py
    word_repository.py
  domain/
    models.py
  services/
    srs_service.py
    training_service.py
    tts_service.py
  ui/
    main_window.py
    theme.py
  utils/
    constants.py
  main.py
```
