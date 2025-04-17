import click
import toml
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from ..templates import (
    load_welcome_content,
    load_base_template,
    load_default_styles,
    load_default_config
)

console = Console()


@click.command()
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

        # Update config with project name
        config = load_default_config()
        config["site_name"] = project_path.name

        # Write files
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            toml.dump(config, f)

        with open(project_path / "content/index.md", "w", 
                  encoding="utf-8") as f:
            f.write(load_welcome_content())

        with open(project_path / "templates/base.html", "w", 
                  encoding="utf-8") as f:
            f.write(load_base_template())

        with open(project_path / "static/css/style.css", "w", 
                  encoding="utf-8") as f:
            f.write(load_default_styles())

        console.print(Panel.fit(
            "[green]Project created successfully![/green]\n\n"
            f"cd {path}\n"
            "staticflow serve",
            title="Next steps"
        ))

    except Exception as e:
        console.print(f"[red]Error creating project:[/red] {str(e)}") 