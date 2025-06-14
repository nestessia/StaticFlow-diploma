---
title: Плагины
date: 2024-03-20
author: nastya
tags: [plugins, extensions, development]
format: markdown
template: page.html
---

# Плагины

В этом разделе мы рассмотрим систему плагинов StaticFlow и как создавать свои плагины.

## Что такое плагин?

Плагин в StaticFlow - это расширение, которое добавляет новую функциональность или изменяет существующую. Плагины могут:

- Добавлять новые форматы контента
- Расширять функциональность шаблонов
- Добавлять новые команды CLI
- Интегрировать внешние сервисы
- Оптимизировать процесс сборки

## Установка плагинов

### Через pip

```bash
pip install staticflow-plugin-name
```

### В конфигурации

```toml
# config.toml
[PLUGINS]
enabled = [
    "plugin-name",
    "another-plugin"
]

[PLUGIN_PLUGIN_NAME]
setting1 = "value1"
setting2 = "value2"
```

## Создание плагина

### 1. Структура плагина

```
my-plugin/
├── staticflow_my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── utils.py
├── tests/
│   └── test_plugin.py
├── setup.py
├── README.md
└── LICENSE
```

### 2. Основной код плагина

```python
# staticflow_my_plugin/plugin.py
from staticflow.plugins import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"
    description = "Описание моего плагина"

    def __init__(self, app):
        super().__init__(app)
        self.settings = app.config.get('PLUGIN_MY_PLUGIN', {})

    def on_build_start(self):
        # Код, выполняемый перед сборкой
        pass

    def on_build_end(self):
        # Код, выполняемый после сборки
        pass

    def on_page_render(self, page, template):
        # Модификация страницы перед рендерингом
        return page, template
```

### 3. Регистрация плагина

```python
# staticflow_my_plugin/__init__.py
from .plugin import MyPlugin

def register(app):
    return MyPlugin(app)
```

### 4. Настройка setup.py

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="staticflow-my-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "staticflow>=1.0.0",
    ],
    entry_points={
        "staticflow.plugins": [
            "my-plugin = staticflow_my_plugin:register",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Описание моего плагина",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/staticflow-my-plugin",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
```

## Типы плагинов

### Плагины контента

```python
class ContentPlugin(Plugin):
    def on_content_load(self, content):
        # Модификация контента
        return content

    def on_content_save(self, content):
        # Обработка перед сохранением
        return content
```

### Плагины шаблонов

```python
class TemplatePlugin(Plugin):
    def on_template_render(self, template, context):
        # Модификация шаблона или контекста
        return template, context

    def register_filters(self, env):
        # Регистрация пользовательских фильтров
        env.filters['my_filter'] = my_filter_function
```

### Плагины CLI

```python
class CLIPlugin(Plugin):
    def register_commands(self, cli):
        @cli.command()
        def my_command():
            """Описание команды"""
            # Код команды
            pass
```

### Плагины сборки

```python
class BuildPlugin(Plugin):
    def on_build_start(self):
        # Подготовка к сборке
        pass

    def on_build_end(self):
        # Очистка после сборки
        pass

    def on_asset_process(self, asset):
        # Обработка ассетов
        return asset
```

## Хуки плагинов

### Хуки жизненного цикла

- `on_init` - инициализация плагина
- `on_build_start` - начало сборки
- `on_build_end` - конец сборки
- `on_clean` - очистка

### Хуки контента

- `on_content_load` - загрузка контента
- `on_content_save` - сохранение контента
- `on_page_render` - рендеринг страницы
- `on_post_render` - рендеринг поста

### Хуки шаблонов

- `on_template_render` - рендеринг шаблона
- `on_template_compile` - компиляция шаблона
- `on_context_update` - обновление контекста

### Хуки ассетов

- `on_asset_process` - обработка ассета
- `on_asset_save` - сохранение ассета
- `on_asset_clean` - очистка ассета

## Конфигурация плагина

### Настройки по умолчанию

```python
class MyPlugin(Plugin):
    default_settings = {
        'option1': 'default1',
        'option2': 'default2',
    }

    def __init__(self, app):
        super().__init__(app)
        self.settings = {
            **self.default_settings,
            **app.config.get('PLUGIN_MY_PLUGIN', {})
        }
```

### Валидация настроек

```python
def validate_settings(self, settings):
    required = ['option1', 'option2']
    for option in required:
        if option not in settings:
            raise ValueError(f"Missing required setting: {option}")
```

## Тестирование плагинов

### Модульные тесты

```python
# tests/test_plugin.py
import pytest
from staticflow_my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin(mock_app)
    assert plugin.name == "my-plugin"
    assert plugin.version == "1.0.0"

def test_plugin_settings():
    plugin = MyPlugin(mock_app)
    assert plugin.settings['option1'] == 'default1'
```

### Интеграционные тесты

```python
def test_plugin_integration():
    app = create_test_app()
    plugin = MyPlugin(app)
    
    # Тестирование функциональности
    result = plugin.process_content("test content")
    assert result == "processed test content"
```

## Публикация плагина

### Подготовка

1. Создайте README.md
2. Добавьте лицензию
3. Напишите документацию
4. Создайте тесты

### Публикация в PyPI

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### Обновление

1. Увеличьте версию
2. Обновите документацию
3. Добавьте миграции
4. Опубликуйте новую версию

## Лучшие практики

### Разработка

1. Следуйте PEP 8
2. Пишите тесты
3. Документируйте код
4. Используйте типизацию

### Производительность

1. Оптимизируйте операции
2. Используйте кэширование
3. Минимизируйте зависимости
4. Следите за памятью

### Безопасность

1. Валидируйте входные данные
2. Используйте безопасные настройки
3. Обрабатывайте ошибки
4. Следите за обновлениями

### Совместимость

1. Поддерживайте версии Python
2. Тестируйте на разных версиях
3. Документируйте зависимости
4. Следите за изменениями API
