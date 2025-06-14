import click
import traceback
from pathlib import Path
from rich.console import Console
from ..core.config import Config
from ..core.server import Server
from ..utils.logging import get_logger

# Получаем логгер для этого модуля
logger = get_logger("cli.serve")

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
            error_message = f"Config file not found: {config}. Check your directory."
            logger.error(error_message)
            console.print(f"[red]Error:[/red] {error_message}")
            return

        server = Server(
            config=Config(config_path),
            host=host,
            port=port,
            dev_mode=True
        )
 
        server.run()

    except Exception as e:
        error_message = f"Error starting server: {str(e)}"
        full_traceback = traceback.format_exc()
        logger.error(error_message)
        logger.error(f"Traceback: {full_traceback}")
        console.print(f"[red]Error starting server:[/red] {str(e)}")
        console.print(f"[dim]Traceback:[/dim]\n{full_traceback}") 