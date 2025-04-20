import click
from rich.console import Console
from .create import create
from .serve import serve
from .deploy import deploy

console = Console()


@click.group()
def cli():
    """StaticFlow - Modern Static Site Generator"""
    pass


# Register commands
cli.add_command(create)
cli.add_command(serve)
cli.add_command(deploy)


if __name__ == '__main__':
    cli()