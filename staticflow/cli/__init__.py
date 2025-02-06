import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich import print as rprint
from ..core.engine import Engine
from ..core.config import Config
from .server import DevServer

console = Console()

@click.group()
def cli():
    """StaticFlow - Modern Static Site Generator"""
    pass

@cli.command()
@click.argument('path')
def create(path: str):
    """Create new StaticFlow project"""
    project_path = Path(path)
    if project_path.exists():
        console.print(f"[red]Error:[/red] Directory {path} already exists")
        return
    
    try:
        # Create project structure
        project_path.mkdir(parents=True)
        (project_path / "content").mkdir()
        (project_path / "templates").mkdir()
        (project_path / "static").mkdir()
        (project_path / "static/css").mkdir(parents=True)
        (project_path / "public").mkdir()
        
        # Create default config
        config = {
            "site_name": project_path.name,
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

        # Create welcome page
        welcome_content = """---
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
$$
\\int_0^\\infty e^{-x} dx = 1
$$

### 3. Диаграммы

```mermaid
graph TD
    A[Начало] --> B[Создание контента]
    B --> C[Сборка сайта]
    C --> D[Публикация]
    D --> E[Конец]
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

        # Create base template
        base_template = """<!DOCTYPE html>
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

        # Create basic styles
        welcome_styles = """/* Base styles */
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
    background: white;
    padding: 1.5rem;
    border: 1px solid var(--border-color);
    border-radius: 0.5rem;
    margin: 1.5rem 0;
}"""

        # Write files
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            import toml
            toml.dump(config, f)

        with open(project_path / "content/index.md", "w", encoding="utf-8") as f:
            f.write(welcome_content)

        with open(project_path / "templates/base.html", "w", encoding="utf-8") as f:
            f.write(base_template)

        with open(project_path / "static/css/style.css", "w", encoding="utf-8") as f:
            f.write(welcome_styles)
            
        console.print(Panel.fit(
            "[green]Project created successfully![/green]\n\n"
            f"cd {path}\n"
            "staticflow serve",
            title="Next steps"
        ))
        
    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {str(e)}")

@cli.command()
@click.option('--config', '-c', default='config.toml', help='Path to config file')
def build(config: str):
    """Build the site"""
    try:
        config_path = Path(config)
        if not config_path.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config}")
            return
            
        with console.status("[bold blue]Building site..."):
            engine = Engine(Config(config_path))
            engine.build()
            
        console.print("[green]Site built successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error building site:[/red] {str(e)}")

@cli.command()
@click.option('--port', '-p', default=8000, help='Port to run server on')
@click.option('--host', '-h', default='localhost', help='Host to run server on')
@click.option('--config', '-c', default='config.toml', help='Path to config file')
def serve(port: int, host: str, config: str):
    """Start development server with hot reload"""
    try:
        config_path = Path(config)
        if not config_path.exists():
            console.print(f"[red]Error:[/red] Config file not found: {config}")
            return
            
        server = DevServer(
            config=Config(config_path),
            host=host,
            port=port
        )
        
        console.print(
            Panel.fit(
                f"[green]Development server running at[/green] http://{host}:{port}\n"
                "[dim]Press CTRL+C to stop[/dim]",
                title="StaticFlow Dev Server"
            )
        )
        
        server.start()
        
    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {str(e)}")

if __name__ == '__main__':
    cli() 