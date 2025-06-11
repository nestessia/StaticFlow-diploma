import click
import traceback
from pathlib import Path
from rich.console import Console
from ..core.config import Config
from ..core.builder import Builder
from ..utils.logging import get_logger

# Получаем логгер для этого модуля
logger = get_logger("cli.build")

console = Console()


@click.command()
@click.option('--config', '-c', default='config.toml', 
              help='Path to config file')
def build(config: str):
    """Build the static site"""
    try:
        config_path = Path(config)
        if not config_path.exists():
            error_message = f"Config file not found: {config}. Check your directory."
            logger.error(error_message)
            console.print(f"[red]Error:[/red] {error_message}")
            return

        builder = Builder(config=Config(config_path))
        builder.build()

        console.print("[green]Build completed successfully![/green]")

    except Exception as e:
        error_message = f"Error building site: {str(e)}"
        full_traceback = traceback.format_exc()
        logger.error(error_message)
        logger.error(f"Traceback: {full_traceback}")
        console.print(f"[red]Error building site:[/red] {str(e)}")
        console.print(f"[dim]Traceback:[/dim]\n{full_traceback}")
