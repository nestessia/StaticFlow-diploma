# Тесты для StaticFlow

Этот каталог содержит тесты для фреймворка StaticFlow.

## Структура тестов

```
tests/
├── unit/                    # Модульные тесты
│   ├── parsers/            # Тесты парсеров
│   ├── deploy/             # Тесты деплоя
│   ├── admin/              # Тесты админ-панели
│   ├── cli/                # Тесты CLI
│   ├── utils/              # Тесты утилит
│   ├── templates/          # Тесты шаблонов
│   ├── plugins/            # Тесты плагинов
│   └── core/               # Тесты ядра
└── integration/            # Интеграционные тесты
```

## Запуск тестов

### Установка зависимостей

```bash
poetry install
```

### Запуск всех тестов

```bash
poetry run pytest
```

### Запуск конкретного теста

```bash
poetry run pytest tests/unit/parsers/test_markdown.py
```

### Запуск тестов с отчетом о покрытии

```bash
poetry run pytest --cov=staticflow --cov-report=html
```

После выполнения этой команды отчет о покрытии будет доступен в директории `htmlcov/`.
