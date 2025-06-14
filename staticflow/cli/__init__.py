import click
from rich.console import Console
from .create import create
from .serve import serve
from .deploy import deploy
from .build import build

console = Console()


@click.group()
def cli():
    """StaticFlow - Modern Static Site Generator"""
    pass


# Register commands
cli.add_command(create)
cli.add_command(serve)
cli.add_command(deploy)
cli.add_command(build)


if __name__ == '__main__':
    cli()
