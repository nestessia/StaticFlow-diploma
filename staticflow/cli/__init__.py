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
        (project_path / "public").mkdir()
        
        # Create default config
        config = {
            "site_name": project_path.name,
            "base_url": "http://localhost:8000",
            "description": "A new StaticFlow site",
            "author": "",
            "language": "en"
        }
        
        with open(project_path / "config.toml", "w", encoding="utf-8") as f:
            import toml
            toml.dump(config, f)
            
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