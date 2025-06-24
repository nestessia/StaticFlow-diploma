---
title: API
date: 2025-05-20
author: nestessia
tags: [api, programming, python, engine]
format: markdown
template: page.html
---

## 🏗️ Программный API

StaticFlow предоставляет мощный API для программного создания и управления сайтами:

```python
from staticflow import Engine, Config, Page
from pathlib import Path

# Создаем конфигурацию
config = Config("config.toml")

# Инициализируем движок
engine = Engine(config)

# Создаем страницу программно
page = Page(
    source_path=Path("programmatic.md"),
    content="# Программно созданная страница\n\nЭта страница создана с помощью Python API.",
    metadata={
        "title": "Программная страница",
        "date": "2023-03-23",
        "tags": ["api", "python"]
    }
)

# Добавляем страницу в движок
engine.site.add_page(page)

# Собираем сайт
engine.build()
```