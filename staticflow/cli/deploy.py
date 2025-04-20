"""
Deploy command for StaticFlow CLI
"""

import click
from rich.console import Console
from rich.prompt import Prompt, Confirm
from pathlib import Path
import os
import json

console = Console()


@click.group(name="deploy")
def deploy():
    """Deploy your site to various platforms."""
    pass


@deploy.command()
@click.argument('platform', type=click.Choice(['github-pages']))
@click.option('--repo-url', help='GitHub repository URL')
@click.option('--branch', help='Branch to deploy to', default='gh-pages')
@click.option('--username', help='GitHub username')
@click.option('--email', help='Git email')
@click.option('--token', help='GitHub token (Personal Access Token)')
@click.option('--cname', help='Custom domain (CNAME)')
@click.option('--message', '-m', help='Commit message')
def setup(platform, repo_url, branch, username, email, token, cname, message):
    """Set up deployment configuration."""
    if platform == 'github-pages':
        setup_github_pages(repo_url, branch, username, email, token, cname)


@deploy.command()
@click.argument('platform', type=click.Choice(['github-pages']))
@click.option('--message', '-m', help='Commit message')
def run(platform, message):
    """Deploy your site to the specified platform."""
    if platform == 'github-pages':
        run_github_pages_deploy(message)


def setup_github_pages(repo_url=None, branch=None, username=None, email=None, token=None, cname=None):
    """Set up GitHub Pages deployment."""
    # Import the deployer here to avoid circular imports
    from ..deploy.github_pages import GitHubPagesDeployer
    
    deployer = GitHubPagesDeployer()
    
    # Get current config
    config = deployer.config
    
    # Interactive setup for missing values
    if not repo_url:
        repo_url = Prompt.ask(
            "GitHub repository URL",
            default=config.get('repo_url', ''),
        )
    
    if not branch:
        branch = Prompt.ask(
            "Branch to deploy to",
            default=config.get('branch', 'gh-pages'),
        )
    
    if not username:
        username = Prompt.ask(
            "GitHub username",
            default=config.get('username', ''),
        )
    
    if not email:
        email = Prompt.ask(
            "Git email",
            default=config.get('email', ''),
        )
    
    if not token and not config.get('token'):
        use_token = Confirm.ask("Do you want to add a GitHub Token (Personal Access Token)?")
        if use_token:
            token = Prompt.ask(
                "GitHub token (Personal Access Token)",
                password=True,
            )
    
    if not cname and Confirm.ask("Do you want to set up a custom domain?", default=False):
        cname = Prompt.ask(
            "Custom domain name",
            default=config.get('cname', ''),
        )
    
    # Update config
    config_data = {
        'repo_url': repo_url,
        'branch': branch,
        'username': username,
        'email': email,
    }
    
    if token:
        config_data['token'] = token
    
    if cname:
        config_data['cname'] = cname
    
    deployer.update_config(**config_data)
    
    # Validate the configuration
    is_valid, errors, warnings = deployer.validate_config()
    
    if not is_valid:
        console.print("[bold red]Configuration is not valid:[/bold red]")
        for error in errors:
            console.print(f"  - {error}")
        return
    
    if warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  - {warning}")
    
    console.print("[bold green]GitHub Pages deployment configured successfully![/bold green]")
    console.print(f"Repository: {repo_url}")
    console.print(f"Branch: {branch}")
    console.print(f"Username: {username}")
    if cname:
        console.print(f"Custom domain: {cname}")
    
    console.print("\nTo deploy your site, run:")
    console.print("[bold]staticflow deploy run github-pages[/bold]")


def run_github_pages_deploy(message=None):
    """Run GitHub Pages deployment."""
    # Import the deployer here to avoid circular imports
    from ..deploy.github_pages import GitHubPagesDeployer
    
    deployer = GitHubPagesDeployer()
    
    # Check if the site is built
    site_path = Path("public")
    if not site_path.exists() or not any(site_path.iterdir()):
        console.print("[bold yellow]Site not built or empty. Building site...[/bold yellow]")
        # Simple build logic - could be replaced with a call to the engine
        os.system("staticflow build")
    
    # Validate the configuration
    is_valid, errors, warnings = deployer.validate_config()
    
    if not is_valid:
        console.print("[bold red]Configuration is not valid:[/bold red]")
        for error in errors:
            console.print(f"  - {error}")
        return False
    
    if warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  - {warning}")
    
    # Deploy the site
    console.print("[bold]Deploying to GitHub Pages...[/bold]")
    
    # Get commit message if not provided
    if not message:
        from datetime import datetime
        message = f"Deployed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    success, deploy_message = deployer.deploy(commit_message=message)
    
    if success:
        console.print(f"[bold green]{deploy_message}[/bold green]")
        return True
    else:
        console.print(f"[bold red]{deploy_message}[/bold red]")
        return False 