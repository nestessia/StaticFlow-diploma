# Документация по настройкам config.toml в StaticFlow

Данный документ содержит подробное описание всех возможных параметров в конфигурационном файле config.toml для фреймворка StaticFlow.

## Содержание
- [Основные параметры](#основные-параметры)
- [Настройки сборки](#настройки-сборки)
- [Настройки многоязычности](#настройки-многоязычности)
- [Настройки плагинов](#настройки-плагинов)
  - [MediaPlugin](#mediaPlugin)
  - [SyntaxHighlightPlugin](#syntaxhighlightplugin)
  - [MathPlugin](#mathplugin)
  - [SEOPlugin](#seoplugin)
  - [SitemapPlugin](#sitemapplugin)
  - [RSSPlugin](#rssplugin)
  - [MinifierPlugin](#minifierplugin)
- [Настройки сервера разработки](#настройки-сервера-разработки)
- [Настройки деплоя](#настройки-деплоя)
- [Полный пример](#полный-пример-configtoml)

## Основные параметры

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `site_name` | строка | Название сайта | `"Мой блог"` |
| `base_url` | строка | Базовый URL сайта (включая протокол) | `"https://mysite.com"` |
| `description` | строка | Описание сайта | `"Персональный блог о технологиях"` |
| `author` | строка | Автор сайта | `"Иван Петров"` |
| `language` | строка | Основной язык сайта (код ISO) | `"ru"` |
| `source_dir` | строка | Директория с исходными файлами | `"content"` |
| `template_dir` | строка | Директория с шаблонами | `"templates"` |
| `static_dir` | строка | Директория со статическими файлами | `"static"` |
| `static_url` | строка | URL-префикс для статических файлов | `"/static"` |
| `output_dir` | строка | Директория для сгенерированного сайта | `"public"` |
| `default_template` | строка | Шаблон по умолчанию | `"page.html"` |

Пример:
```toml
site_name = "StaticFlow Blog"
base_url = "https://example.com"
description = "Современный статический сайт"
author = "Иван Петров"
language = "ru"
source_dir = "content"
template_dir = "templates"
static_dir = "static"
static_url = "/static"
output_dir = "public"
default_template = "page.html"
```

## Настройки сборки

Настройки процесса сборки сайта задаются в секции `[build]`:

```toml
[build]
clean_before = true           # Очистка директории перед сборкой
exclude_patterns = [".*", "_*"]  # Шаблоны исключения файлов
include_drafts = false        # Включение черновиков
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `clean_before` | булев | Очищать директорию перед сборкой | `true` |
| `exclude_patterns` | список строк | Шаблоны для исключения файлов | `[".*", "_*"]` |
| `include_drafts` | булев | Включать черновики (draft: true) | `false` |
| `parallel` | булев | Включить параллельную обработку | `true` |

## Настройки многоязычности

Параметры для многоязычных сайтов задаются в секции `[languages]`:

```toml
[languages]
default = "ru"                # Язык по умолчанию
enabled = ["ru", "en", "fr"]  # Поддерживаемые языки
use_language_prefixes = true  # Использовать префиксы языков в URL
exclude_default_lang_prefix = true  # Исключать префикс для языка по умолчанию
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `default` | строка | Язык по умолчанию | `"ru"` |
| `enabled` | список строк | Поддерживаемые языки | `["ru", "en", "fr"]` |
| `use_language_prefixes` | булев | Добавлять префиксы языка в URL | `true` |
| `exclude_default_lang_prefix` | булев | Не добавлять префикс для языка по умолчанию | `true` |
| `fallback` | строка | Язык для запасного контента | `"en"` |

## Настройки плагинов

Список активных плагинов указывается в секции `[plugins]`:

```toml
[plugins]
enabled = ["media", "syntax_highlight", "math", "seo", "sitemap", "rss", "minifier"]
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `enabled` | список строк | Включенные плагины | `["media", "seo"]` |

### MediaPlugin

Плагин для обработки изображений, видео и других медиафайлов:

```toml
[plugins.media]
output_dir = "media"          # Директория для обработанных медиафайлов
source_dir = "static"         # Исходная директория с медиафайлами
sizes = {                     # Размеры изображений для генерации
  thumbnail = { width = 200, height = 200, quality = 70 },
  small = { width = 400, quality = 80 },
  medium = { width = 800, quality = 85 },
  large = { width = 1200, quality = 90 },
  original = { quality = 95 }
}
formats = ["webp", "original"]  # Форматы для генерации
generate_placeholders = true    # Генерировать плейсхолдеры
placeholder_size = 20           # Размер плейсхолдера в пикселях
process_videos = true           # Обрабатывать видео
video_thumbnail = true          # Создавать миниатюры для видео
hash_filenames = true           # Добавлять хеш к именам файлов
hash_length = 8                 # Длина хеша
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `output_dir` | строка | Выходная директория для медиафайлов | `"media"` |
| `source_dir` | строка | Исходная директория | `"static"` |
| `sizes` | объект | Настройки размеров изображений | См. пример выше |
| `formats` | список строк | Форматы для генерации | `["webp", "original"]` |
| `generate_placeholders` | булев | Генерировать плейсхолдеры | `true` |
| `placeholder_size` | число | Ширина плейсхолдера в пикселях | `20` |
| `process_videos` | булев | Обрабатывать видеофайлы | `true` |
| `video_thumbnail` | булев | Генерировать миниатюры для видео | `true` |
| `hash_filenames` | булев | Добавлять хеш к именам файлов | `true` |
| `hash_length` | число | Длина хеша в имени файла | `8` |

### SyntaxHighlightPlugin

Плагин для подсветки синтаксиса кода:

```toml
[plugins.syntax_highlight]
style = "monokai"           # Стиль подсветки
linenums = false            # Показывать номера строк
css_class = "highlight"     # CSS-класс для блока кода
tabsize = 4                 # Размер табуляции
preserve_tabs = true        # Сохранять табуляцию
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `style` | строка | Тема подсветки синтаксиса | `"monokai"` |
| `linenums` | булев | Показывать номера строк | `false` |
| `css_class` | строка | CSS-класс для блока кода | `"highlight"` |
| `tabsize` | число | Размер табуляции | `4` |
| `preserve_tabs` | булев | Сохранять табуляцию | `true` |

### MathPlugin

Плагин для отображения математических формул:

```toml
[plugins.math]
auto_render = true          # Автоматический рендеринг формул
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `auto_render` | булев | Автоматический рендеринг формул | `true` |
| `delimiter_inline` | список строк | Разделители для инлайн-формул | `["$", "$"]` |
| `delimiter_block` | список строк | Разделители для блочных формул | `["$$", "$$"]` |

### SEOPlugin

Плагин для улучшения SEO-оптимизации:

```toml
[plugins.seo]
twitter_card = true         # Добавлять Twitter Card мета-теги
open_graph = true           # Добавлять Open Graph мета-теги
structured_data = true      # Добавлять структурированные данные
robots_txt = true           # Генерировать robots.txt
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `twitter_card` | булев | Добавлять Twitter Card мета-теги | `true` |
| `open_graph` | булев | Добавлять Open Graph мета-теги | `true` |
| `structured_data` | булев | Добавлять структурированные данные | `true` |
| `robots_txt` | булев | Генерировать robots.txt | `true` |
| `canonical_urls` | булев | Добавлять canonical URL | `true` |

### SitemapPlugin

Плагин для генерации карты сайта (sitemap.xml):

```toml
[plugins.sitemap]
priority = 0.8              # Приоритет по умолчанию
changefreq = "weekly"       # Частота изменений по умолчанию
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `priority` | число | Приоритет по умолчанию | `0.8` |
| `changefreq` | строка | Частота изменений | `"weekly"` |
| `exclude_patterns` | список строк | Шаблоны исключения URLs | `["*.pdf", "/admin/*"]` |

### RSSPlugin

Плагин для генерации RSS-ленты:

```toml
[plugins.rss]
site_name = "Мой сайт"
site_description = "Описание"
language = "ru"
items_count = 20           # Количество записей в ленте
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `site_name` | строка | Название сайта для RSS | `"Мой блог"` |
| `site_description` | строка | Описание сайта для RSS | `"Персональный блог"` |
| `language` | строка | Язык ленты | `"ru"` |
| `items_count` | число | Количество записей | `20` |
| `feed_filename` | строка | Имя файла RSS | `"feed.xml"` |

### MinifierPlugin

Плагин для минификации HTML, CSS и JavaScript:

```toml
[plugins.minifier]
minify_html = true          # Минифицировать HTML
minify_css = true           # Минифицировать CSS
minify_js = true            # Минифицировать JavaScript
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `minify_html` | булев | Минифицировать HTML | `true` |
| `minify_css` | булев | Минифицировать CSS | `true` |
| `minify_js` | булев | Минифицировать JavaScript | `true` |
| `remove_comments` | булев | Удалять комментарии | `true` |
| `exclude_patterns` | список строк | Шаблоны исключения файлов | `["*.min.js"]` |

## Настройки сервера разработки

Настройки для локального сервера разработки:

```toml
[server]
host = "127.0.0.1"          # Хост для сервера разработки
port = 8000                 # Порт для сервера разработки
live_reload = true          # Включить автоматическую перезагрузку
browser_open = true         # Автоматически открывать браузер
watch_paths = ["content", "templates", "static"]  # Отслеживаемые директории
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `host` | строка | Хост для сервера разработки | `"127.0.0.1"` |
| `port` | число | Порт для сервера разработки | `8000` |
| `live_reload` | булев | Автоматическая перезагрузка | `true` |
| `browser_open` | булев | Автоматически открывать браузер | `true` |
| `watch_paths` | список строк | Отслеживаемые директории | `["content", "templates"]` |

## Настройки деплоя

Настройки для развертывания сайта:

```toml
[deploy.github_pages]
repo = "username/repo"      # Репозиторий GitHub
branch = "gh-pages"         # Ветка для деплоя
cname = "example.com"       # Настройка CNAME
```

| Параметр | Тип | Описание | Пример |
|----------|-----|----------|--------|
| `repo` | строка | URL или путь к репозиторию | `"username/repo"` |
| `branch` | строка | Ветка для деплоя | `"gh-pages"` |
| `cname` | строка | Настройка CNAME | `"example.com"` |
| `clean` | булев | Очищать ветку перед деплоем | `true` |
| `message` | строка | Коммит-сообщение | `"Site updated: {date}"` |

## Полный пример config.toml

Ниже приведен пример полного конфигурационного файла со всеми доступными настройками:

```toml
# Основные настройки
site_name = "StaticFlow Blog"
base_url = "https://example.com"
description = "Современный статический сайт на StaticFlow"
author = "Иван Петров"
language = "ru"
source_dir = "content"
template_dir = "templates"
static_dir = "static"
static_url = "/static"
output_dir = "public"
default_template = "page.html"

# Настройки сборки
[build]
clean_before = true
exclude_patterns = [".*", "_*"]
include_drafts = false
parallel = true

# Языки
[languages]
default = "ru"
enabled = ["ru", "en"]
use_language_prefixes = true
exclude_default_lang_prefix = true

# Плагины
[plugins]
enabled = ["media", "syntax_highlight", "math", "seo", "sitemap", "rss", "minifier"]

# Настройки MediaPlugin
[plugins.media]
output_dir = "media"
source_dir = "static"
sizes = { 
  thumbnail = { width = 200, height = 200, quality = 70 },
  small = { width = 400, quality = 80 },
  medium = { width = 800, quality = 85 },
  large = { width = 1200, quality = 90 },
  original = { quality = 95 }
}
formats = ["webp", "original"]
generate_placeholders = true
placeholder_size = 20
process_videos = true
video_thumbnail = true
hash_filenames = true
hash_length = 8

# Настройки SyntaxHighlightPlugin
[plugins.syntax_highlight]
style = "monokai"
linenums = false
css_class = "highlight"
tabsize = 4
preserve_tabs = true

# Настройки MathPlugin
[plugins.math]
auto_render = true
delimiter_inline = ["$", "$"]
delimiter_block = ["$$", "$$"]

# Настройки SEOPlugin
[plugins.seo]
twitter_card = true
open_graph = true
structured_data = true
robots_txt = true
canonical_urls = true

# Настройки SitemapPlugin
[plugins.sitemap]
priority = 0.8
changefreq = "weekly"
exclude_patterns = ["*.pdf", "/admin/*"]

# Настройки RSSPlugin
[plugins.rss]
site_name = "Мой блог"
site_description = "Персональный блог о технологиях"
language = "ru"
items_count = 20
feed_filename = "feed.xml"

# Настройки MinifierPlugin
[plugins.minifier]
minify_html = true
minify_css = true
minify_js = true
remove_comments = true
exclude_patterns = ["*.min.js"]

# Настройки сервера разработки
[server]
host = "127.0.0.1"
port = 8000
live_reload = true
browser_open = true
watch_paths = ["content", "templates", "static"]

# Настройки деплоя
[deploy.github_pages]
repo = "username/repo"
branch = "gh-pages"
cname = "example.com"
clean = true
message = "Site updated: {date}"
```

## Использование переменных окружения

StaticFlow также поддерживает использование переменных окружения в config.toml с помощью синтаксиса `${ENV_VAR}`:

```toml
# Использование переменной окружения для токена GitHub
[deploy.github_pages]
token = "${GITHUB_TOKEN}"
```

## Условные настройки для разных окружений

Для разных окружений можно использовать разные конфигурации:

```toml
# Разные настройки в зависимости от окружения
[production]
base_url = "https://example.com"

[development]
base_url = "http://localhost:8000"
```

Для выбора окружения используется параметр `--env` при запуске команд StaticFlow:

```bash
staticflow build --env production
``` 