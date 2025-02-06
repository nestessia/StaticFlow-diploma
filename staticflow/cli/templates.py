"""Default templates and content for new projects."""

WELCOME_CONTENT = """---
title: Welcome to StaticFlow
template: base.html
---
# Добро пожаловать в StaticFlow!

StaticFlow - это современный генератор статических сайтов с богатыми возможностями для создания контента.

## Возможности

### 1. Подсветка кода

```python
def hello_world():
    print("Привет, StaticFlow!")
```

### 2. Математические формулы

Inline формула: $E = mc^2$

Блочная формула:
$
\\int_0^\\infty e^{-x} dx = 1
$

### 3. Диаграммы

```mermaid
graph TD;
    A[Начало] --> B[Создание контента];
    B --> C[Сборка сайта];
    C --> D[Публикация];
    D --> E[Конец];
```

### 4. Блоки в стиле Notion

:::info Информация
Это информационный блок. Используйте его для важных заметок.
:::

:::warning Предупреждение
Это блок с предупреждением. Обратите особое внимание!
:::

## Начало работы

1. Создание контента:
   - Добавьте Markdown файлы в директорию `content`
   - Используйте front matter для метаданных

2. Настройка шаблонов:
   - Измените шаблоны в директории `templates`
   - Добавьте свои стили в `static/css`

3. Запуск сервера разработки:
```bash
staticflow serve
```"""

BASE_TEMPLATE = """<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
    {{ page.head_content }}
</head>
<body>
    <header>
        <div class="container">
            <h1>{{ page.title }}</h1>
        </div>
    </header>
    <main>
        <div class="container">
            {{ page.content }}
        </div>
    </main>
    <footer>
        <div class="container">
            <p>Powered by StaticFlow</p>
        </div>
    </footer>
</body>
</html>"""

DEFAULT_STYLES = """/* Base styles */
:root {
    --primary-color: #3b82f6;
    --text-color: #1f2937;
    --bg-color: #ffffff;
    --code-bg: #f8fafc;
    --border-color: #e5e7eb;
    --container-width: 800px;
}

body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.6;
    color: var(--text-color);
    background: var(--bg-color);
    margin: 0;
    padding: 0;
}

.container {
    max-width: var(--container-width);
    margin: 0 auto;
    padding: 0 1.5rem;
}

header {
    background: var(--primary-color);
    color: white;
    padding: 2rem 0;
    margin-bottom: 2rem;
}

header h1 {
    margin: 0;
    font-size: 2.5rem;
    font-weight: 700;
}

main {
    min-height: calc(100vh - 300px);
    padding: 2rem 0;
}

footer {
    background: var(--code-bg);
    color: var(--text-color);
    padding: 2rem 0;
    margin-top: 4rem;
    text-align: center;
}

h1, h2, h3 {
    color: var(--primary-color);
    margin-top: 2rem;
    margin-bottom: 1rem;
}

h1 {
    font-size: 2.5rem;
    border-bottom: 2px solid var(--primary-color);
    padding-bottom: 0.5rem;
}

h2 {
    font-size: 2rem;
}

h3 {
    font-size: 1.5rem;
}

p {
    margin: 1rem 0;
}

code {
    background: var(--code-bg);
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: monospace;
}

pre {
    background: var(--code-bg);
    padding: 1.5rem;
    border-radius: 0.5rem;
    overflow-x: auto;
    margin: 1.5rem 0;
}

/* Plugin-specific styles */
.highlight {
    margin: 1.5rem 0;
    border-radius: 0.5rem;
    overflow: hidden;
}

.mermaid {
    text-align: center;
    background: white;
    padding: 2rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    margin: 1.5rem 0;
}

.mermaid svg {
    max-width: 100%;
    height: auto;
}"""

DEFAULT_CONFIG = {
    "site_name": "",  # Will be set to project name
    "base_url": "http://localhost:8000",
    "description": "A new StaticFlow site",
    "author": "",
    "language": "ru",
    
    # Directories
    "source_dir": "content",
    "template_dir": "templates",
    "static_dir": "static",
    "output_dir": "public",
    
    # Default settings
    "default_template": "base.html",
    
    # Plugin settings
    "plugins": {
        "syntax_highlight": {
            "style": "monokai",
            "line_numbers": True
        },
        "math": {
            "auto_render": True
        },
        "diagrams": {
            "theme": "default"
        },
        "notion_blocks": {
            "enabled": True
        }
    }
} 