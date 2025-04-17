import click
from rich.console import Console
from .create import create
from .serve import serve

console = Console()


@click.group()
def cli():
    """StaticFlow - Modern Static Site Generator"""
    pass


# Register commands
cli.add_command(create)
cli.add_command(serve)


if __name__ == '__main__':
    cli()