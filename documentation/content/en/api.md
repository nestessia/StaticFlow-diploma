---
title: API
date: 2025-05-20
author: nestessia
tags: [api, programming, python, engine]
format: markdown
template: en_page.html
language: en
---

## 🏗️ Programmatic API

StaticFlow provides a powerful API for programmatic site creation and management:

```python
from staticflow import Engine, Config, Page
from pathlib import Path

# Create configuration
config = Config("config.toml")

# Initialize engine
engine = Engine(config)

# Create page programmatically
page = Page(
    source_path=Path("programmatic.md"),
    content="# Programmatically Created Page\n\nThis page was created using the Python API.",
    metadata={
        "title": "Programmatic Page",
        "date": "2023-03-23",
        "tags": ["api", "python"]
    }
)

# Add page to engine
engine.site.add_page(page)

# Build site
engine.build()
```