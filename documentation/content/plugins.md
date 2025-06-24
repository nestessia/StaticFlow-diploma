---
title: Плагины
date: 2025-05-20
author: nestessia
tags: [plugins, extensions, development]
format: markdown
template: page.html
---

# 🔌 Плагины

В этом разделе мы рассмотрим систему плагинов StaticFlow и как создавать свои плагины.

## 🤔 Что такое плагин?

Плагин в StaticFlow - это расширение, которое добавляет новую функциональность или изменяет существующую. Плагины могут:

- ✨ Добавлять новые форматы контента
- 🎨 Расширять функциональность шаблонов
- 🖥️ Добавлять новые команды CLI
- 🔗 Интегрировать внешние сервисы
- ⚡ Оптимизировать процесс сборки
- 🖼️ Обрабатывать медиафайлы
- 🌐 Поддерживать многоязычность

## 🏗️ Архитектура системы плагинов

### Основные компоненты

#### **Plugin (Базовый класс)**
```python
class Plugin(ABC):
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.enabled: bool = True
        self._hooks: Dict[HookType, List[str]] = {}
```

#### **PluginMetadata (Метаданные)**
```python
@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None
    requires_config: bool = False
    priority: int = 100
```

#### **HookType (Типы хуков)**
```python
class HookType(Enum):
    PRE_BUILD = auto()          # Перед сборкой сайта
    POST_BUILD = auto()         # После сборки сайта
    PRE_PAGE = auto()          # Перед обработкой страницы
    POST_PAGE = auto()         # После обработки страницы
    PRE_TEMPLATE = auto()      # Перед рендерингом шаблона
    POST_TEMPLATE = auto()     # После рендеринга шаблона
    PRE_ASSET = auto()         # Перед обработкой ресурса
    POST_ASSET = auto()        # После обработки ресурса
```

## 📦 Установка плагинов

### Через pip

```bash
pip install staticflow-plugin-name
```

### В конфигурации

```toml
# config.toml
[PLUGINS]
enabled = [
    "syntax_highlight",
    "math",
    "media",
    "cdn",
    "seo"
]

[PLUGIN_SYNTAX_HIGHLIGHT]
style = "monokai"
linenums = false
css_class = "highlight"

[PLUGIN_MEDIA]
output_dir = "media"
sizes = { "thumbnail" = { width = 200, height = 200 } }
formats = ["webp", "original"]
```

## 🛠️ Создание плагина

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
from staticflow.plugins.core.base import Plugin, PluginMetadata
from typing import Dict, Any

class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="Описание моего плагина",
            author="Your Name",
            requires_config=False,
            priority=100
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Инициализация плагина."""
        super().initialize(config)
        # Ваша логика инициализации
    
    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Хук перед сборкой сайта."""
        # Подготовка к сборке
        return context
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Хук после обработки страницы."""
        # Модификация контента страницы
        content = context.get('content', '')
        # Ваша обработка контента
        context['content'] = content
        return context
    
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Хук перед обработкой ресурса."""
        # Обработка статических файлов
        return context
    
    def cleanup(self) -> None:
        """Очистка ресурсов плагина."""
        # Очистка ресурсов
        pass
```

### 3. Регистрация плагина

```python
# staticflow_my_plugin/__init__.py
from .plugin import MyPlugin

def register(engine):
    plugin = MyPlugin()
    engine.add_plugin(plugin)
    return plugin
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

## 🎯 Типы плагинов

### 📝 Плагины контента

```python
class ContentPlugin(Plugin):
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка контента страницы."""
        content = context.get('content', '')
        # Модификация контента
        context['content'] = processed_content
        return context
```

### 🎨 Плагины шаблонов

```python
class TemplatePlugin(Plugin):
    def on_post_template(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Обработка после рендеринга шаблона."""
        # Модификация контекста или шаблона
        return context
```

### 🖥️ Плагины CLI

```python
class CLIPlugin(Plugin):
    def register_commands(self, cli):
        @cli.command()
        def my_command():
            """Описание команды"""
            # Код команды
            pass
```

### ⚡ Плагины сборки

```python
class BuildPlugin(Plugin):
    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Подготовка к сборке."""
        # Подготовка ресурсов
        return context
    
    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Очистка после сборки."""
        # Очистка временных файлов
        return context
```

## 🔗 Хуки плагинов

### 🔄 Хуки жизненного цикла

- `on_pre_build` - перед сборкой сайта
- `on_post_build` - после сборки сайта
- `initialize` - инициализация плагина
- `cleanup` - очистка ресурсов

### 📄 Хуки страниц

- `on_pre_page` - перед обработкой страницы
- `on_post_page` - после обработки страницы
- `process_content` - обработка контента

### 🎨 Хуки шаблонов

- `on_pre_template` - перед рендерингом шаблона
- `on_post_template` - после рендеринга шаблона

### 📁 Хуки ресурсов

- `on_pre_asset` - перед обработкой ресурса
- `on_post_asset` - после обработки ресурса

## ⚙️ Конфигурация плагина

### Настройки по умолчанию

```python
class MyPlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        default_config = {
            'option1': 'default1',
            'option2': 'default2',
        }
        
        # Объединение с пользовательской конфигурацией
        self.config = {**default_config, **(config or {})}
        super().initialize()
```

### Валидация настроек

```python
def validate_config(self) -> bool:
    """Проверка конфигурации плагина."""
    required = ['option1', 'option2']
    for option in required:
        if option not in self.config:
            raise ValueError(f"Missing required setting: {option}")
    return True
```

## 🧪 Тестирование плагинов

### Модульные тесты

```python
# tests/test_plugin.py
import pytest
from staticflow_my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    assert plugin.metadata.name == "my-plugin"
    assert plugin.metadata.version == "1.0.0"

def test_plugin_config():
    config = {'option1': 'value1'}
    plugin = MyPlugin()
    plugin.initialize(config)
    assert plugin.config['option1'] == 'value1'

def test_plugin_hooks():
    plugin = MyPlugin()
    context = {'content': 'test content'}
    
    # Тестирование хука
    result = plugin.on_post_page(context)
    assert 'content' in result
```

### Интеграционные тесты

```python
def test_plugin_integration():
    from staticflow.core.engine import Engine
    from staticflow.core.config import Config
    
    # Создание тестового движка
    config = Config("test_config.toml")
    engine = Engine(config)
    
    # Добавление плагина
    plugin = MyPlugin()
    engine.add_plugin(plugin)
    
    # Тестирование функциональности
    assert engine.get_plugin("my-plugin") == plugin
```

## 📦 Встроенные плагины

### 🔍 SEO Plugin
```python
# Автоматическое добавление Open Graph тегов
# Twitter Card тегов
# Schema.org разметки
# Оптимизация заголовков и изображений
```

### 🗺️ Sitemap Plugin
```python
# Генерация sitemap.xml
# Автоматическое обновление
# Поддержка приоритетов
```

### 📡 RSS Plugin
```python
# Генерация RSS лент
# Поддержка категорий
# Автоматическое обновление
```

### 🖼️ Media Plugin
```python
# Обработка изображений
# Генерация WebP
# Создание srcset
# Оптимизация видео
```

### 🌐 CDN Plugin
```python
# Интеграция с CDN
# Автоматическая загрузка файлов
# Очистка кэша
```

### 💎 Syntax Highlight Plugin
```python
# Подсветка синтаксиса кода
# Поддержка множества языков
# Кастомизируемые темы
```

### ➗ Math Plugin
```python
# Рендеринг математических формул
# Поддержка LaTeX
# Автоматическое рендеринг
```

### 📊 Mermaid Plugin
```python
# Создание диаграмм
# Поддержка различных типов
# Интерактивные диаграммы
```

## 🚀 Публикация плагина

### Подготовка

1. 📝 Создайте README.md
2. 📄 Добавьте лицензию
3. 📚 Напишите документацию
4. 🧪 Создайте тесты
5. 🔧 Настройте CI/CD

### Публикация в PyPI

```bash
# Сборка пакета
python setup.py sdist bdist_wheel

# Загрузка в PyPI
twine upload dist/*
```

### Обновление

1. 🔢 Увеличьте версию
2. 📚 Обновите документацию
3. 🔄 Добавьте миграции
4. 🚀 Опубликуйте новую версию

## 💡 Лучшие практики

### 🛠️ Разработка

1. 📏 Следуйте PEP 8
2. 🧪 Пишите тесты
3. 📝 Документируйте код
4. 🏷️ Используйте типизацию
5. 🔍 Обрабатывайте ошибки

### ⚡ Производительность

1. 🚀 Оптимизируйте операции
2. 💾 Используйте кэширование
3. 📦 Минимизируйте зависимости
4. 💻 Следите за памятью
5. 🔄 Используйте асинхронность

### 🔒 Безопасность

1. ✅ Валидируйте входные данные
2. 🔐 Используйте безопасные настройки
3. ⚠️ Обрабатывайте ошибки
4. 🔄 Следите за обновлениями
5. 🛡️ Проверяйте зависимости

### 🔗 Совместимость

1. 🐍 Поддерживайте версии Python
2. 🧪 Тестируйте на разных версиях
3. 📋 Документируйте зависимости
4. 👀 Следите за изменениями API
5. 🔄 Обеспечивайте обратную совместимость

## 🎯 Примеры использования

### Простой плагин для добавления мета-тегов

```python
class MetaTagsPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="meta-tags",
            version="1.0.0",
            description="Добавляет мета-теги к страницам",
            author="Your Name"
        )
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context.get('content', '')
        
        # Добавляем мета-теги
        meta_tags = f"""
        <meta name="generator" content="StaticFlow">
        <meta name="author" content="{context.get('author', 'Unknown')}">
        <meta name="date" content="{context.get('date', '')}">
        """
        
        # Вставляем в head
        if '<head>' in content:
            content = content.replace('<head>', f'<head>{meta_tags}')
        
        context['content'] = content
        return context
```

### Плагин для обработки изображений

```python
class ImageProcessorPlugin(Plugin):
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        file_path = context.get('file_path')
        
        if self._is_image(file_path):
            # Обработка изображения
            processed_path = self._process_image(file_path)
            context['file_path'] = processed_path
        
        return context
    
    def _is_image(self, path: str) -> bool:
        return path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    
    def _process_image(self, path: str) -> str:
        # Логика обработки изображения
        return path
```
