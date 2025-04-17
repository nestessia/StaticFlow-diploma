import click
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from ..core.config import Config
from ..core.server import Server

console = Console()


@click.command()
@click.option('--port', '-p', default=8000, help='Port to run server on')
@click.option('--host', '-h', default='localhost', 
              help='Host to run server on')
@click.option('--config', '-c', default='config.toml', 
              help='Path to config file')
def serve(port: int, host: str, config: str):
    """Start development server with live preview"""
    try:
        config_path = Path(config)
        if not config_path.exists():
            console.print(
                f"[red]Error:[/red] Config file not found: {config}. "
                "Check your directory."
            )
            return

        server = Server(
            config=Config(config_path),
            host=host,
            port=port,
            dev_mode=True
        )
 
        console.print(
            Panel.fit(
                f"[green]Server running at[/green] http://{host}:{port}\n"
                "[dim]Press CTRL+C to stop[/dim]",
                title="StaticFlow Dev Server"
            )
        )

        server.run()

    except Exception as e:
        console.print(f"[red]Error starting server:[/red] {str(e)}") 