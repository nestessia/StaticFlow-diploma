---
title: API Reference
date: 2024-03-20
author: nastya
tags: [api, development, reference]
format: markdown
template: page.html
---

# API документация

В этом разделе мы рассмотрим API StaticFlow для разработчиков.

## Основные классы

### Application

Основной класс приложения.

```python
from staticflow import Application

app = Application(
    content_dir="content",
    output_dir="output",
    static_dir="static",
    templates_dir="templates"
)
```

#### Методы

- `build()` - сборка сайта
- `clean()` - очистка выходной директории
- `serve(host='localhost', port=8000)` - запуск сервера разработки

#### Свойства

- `config` - конфигурация приложения
- `content` - менеджер контента
- `templates` - менеджер шаблонов
- `plugins` - менеджер плагинов

### Content

Управление контентом.

```python
from staticflow import Content

content = Content(app)
```

#### Методы

- `load(path)` - загрузка контента
- `save(content, path)` - сохранение контента
- `get(path)` - получение страницы
- `list(path='')` - список страниц
- `search(query)` - поиск по контенту

#### Свойства

- `pages` - все страницы
- `posts` - все посты
- `categories` - категории
- `tags` - теги

### Template

Управление шаблонами.

```python
from staticflow import Template

template = Template(app)
```

#### Методы

- `render(template_name, context)` - рендеринг шаблона
- `get_template(name)` - получение шаблона
- `register_filter(name, func)` - регистрация фильтра
- `register_function(name, func)` - регистрация функции

#### Свойства

- `env` - окружение Jinja2
- `filters` - доступные фильтры
- `functions` - доступные функции

### Plugin

Базовый класс для плагинов.

```python
from staticflow import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"

    def on_build_start(self):
        pass

    def on_build_end(self):
        pass
```

#### Методы

- `on_init()` - инициализация
- `on_build_start()` - начало сборки
- `on_build_end()` - конец сборки
- `on_clean()` - очистка

## Модели данных

### Page

Модель страницы.

```python
from staticflow import Page

page = Page(
    title="Заголовок",
    content="Содержимое",
    template="page.html",
    date="2024-03-20"
)
```

#### Свойства

- `title` - заголовок
- `content` - содержимое
- `template` - шаблон
- `date` - дата
- `author` - автор
- `tags` - теги
- `category` - категория
- `url` - URL страницы
- `slug` - URL-friendly версия заголовка

### Post

Модель поста (наследуется от Page).

```python
from staticflow import Post

post = Post(
    title="Заголовок поста",
    content="Содержимое поста",
    date="2024-03-20",
    author="Автор"
)
```

#### Дополнительные свойства

- `excerpt` - отрывок
- `comments` - комментарии
- `related` - связанные посты

### Category

Модель категории.

```python
from staticflow import Category

category = Category(
    name="Название",
    description="Описание",
    parent=None
)
```

#### Свойства

- `name` - название
- `description` - описание
- `parent` - родительская категория
- `children` - дочерние категории
- `posts` - посты в категории
- `url` - URL категории

### Tag

Модель тега.

```python
from staticflow import Tag

tag = Tag(name="python")
```

#### Свойства

- `name` - название
- `posts` - посты с тегом
- `url` - URL тега

## Утилиты

### Markdown

Работа с Markdown.

```python
from staticflow.utils.markdown import Markdown

md = Markdown()
html = md.convert("# Заголовок")
```

#### Методы

- `convert(text)` - конвертация в HTML
- `convert_file(path)` - конвертация файла
- `register_extension(ext)` - регистрация расширения

### Assets

Управление ассетами.

```python
from staticflow.utils.assets import Assets

assets = Assets(app)
```

#### Методы

- `process(path)` - обработка ассета
- `optimize(path)` - оптимизация
- `minify(path)` - минификация
- `hash(path)` - хеширование

### Cache

Управление кэшем.

```python
from staticflow.utils.cache import Cache

cache = Cache(app)
```

#### Методы

- `get(key)` - получение из кэша
- `set(key, value)` - сохранение в кэш
- `delete(key)` - удаление из кэша
- `clear()` - очистка кэша

## CLI

### Команды

```python
from staticflow.cli import cli

@cli.command()
def my_command():
    """Описание команды"""
    pass
```

#### Встроенные команды

- `build` - сборка сайта
- `serve` - запуск сервера
- `clean` - очистка
- `new` - создание проекта
- `new-page` - создание страницы
- `new-post` - создание поста

### Аргументы

```python
@cli.command()
@click.option('--output', '-o', help='Выходная директория')
def build(output):
    pass
```

## События

### Регистрация обработчика

```python
@app.on('build_start')
def on_build_start():
    pass
```

### Доступные события

- `init` - инициализация
- `build_start` - начало сборки
- `build_end` - конец сборки
- `clean` - очистка
- `content_load` - загрузка контента
- `content_save` - сохранение контента
- `template_render` - рендеринг шаблона
- `page_render` - рендеринг страницы
- `post_render` - рендеринг поста

## Конфигурация

### Загрузка конфигурации

```python
from staticflow.config import Config

config = Config('config.toml')
```

### Настройки

```toml
# config.toml
site_name = "My Site"
base_url = "http://example.com"
language = "ru"

[build]
output_dir = "output"
clean = true

[server]
host = "localhost"
port = 8000
```

## Расширения

### Создание расширения

```python
from staticflow.extensions import Extension

class MyExtension(Extension):
    def init_app(self, app):
        pass
```

### Регистрация расширения

```python
app.register_extension(MyExtension())
```

## Тестирование

### Тестовое приложение

```python
from staticflow.testing import TestApp

app = TestApp()
```

### Тестовый клиент

```python
client = app.test_client()
response = client.get('/')
```

### Фикстуры

```python
@pytest.fixture
def app():
    return TestApp()

@pytest.fixture
def client(app):
    return app.test_client()
```

## Отладка

### Логирование

```python
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('staticflow')
```

### Профилирование

```python
from staticflow.utils.profiler import Profiler

with Profiler() as profiler:
    app.build()
```

## Безопасность

### Валидация

```python
from staticflow.utils.validator import Validator

validator = Validator()
validator.validate_page(page)
```

### Санитизация

```python
from staticflow.utils.sanitizer import Sanitizer

sanitizer = Sanitizer()
clean_html = sanitizer.sanitize(html)
```

## Интернационализация

### Переводы

```python
from staticflow.utils.i18n import I18n

i18n = I18n(app)
text = i18n.translate('hello', 'ru')
```

### Форматирование

```python
from staticflow.utils.i18n import format_date

date = format_date('2024-03-20', 'ru')
```

## Поиск

### Индексация

```python
from staticflow.utils.search import Search

search = Search(app)
search.index_page(page)
```

### Поиск

```python
results = search.search('запрос')
```

## Кэширование

### Страницы

```python
from staticflow.utils.cache import PageCache

cache = PageCache(app)
cache.set(page)
```

### Ассеты

```python
from staticflow.utils.cache import AssetCache

cache = AssetCache(app)
cache.set(asset)
```

## Оптимизация

### Изображения

```python
from staticflow.utils.optimizer import ImageOptimizer

optimizer = ImageOptimizer(app)
optimizer.optimize(image_path)
```

### CSS/JS

```python
from staticflow.utils.optimizer import AssetOptimizer

optimizer = AssetOptimizer(app)
optimizer.minify(css_path)
```

## Мониторинг

### Метрики

```python
from staticflow.utils.metrics import Metrics

metrics = Metrics(app)
metrics.record_build_time(time)
```

### Логи

```python
from staticflow.utils.logger import Logger

logger = Logger(app)
logger.info('Сообщение')
``` 