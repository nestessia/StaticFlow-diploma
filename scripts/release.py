#!/usr/bin/env python
import subprocess
import sys
from pathlib import Path
from rich.console import Console
from rich.panel import Panel

console = Console()


def run_command(command: str) -> bool:
    """Run a shell command and return success status."""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False


def check_code_quality():
    """Check code quality."""
    console.print("\n[bold blue]Checking code quality...[/bold blue]")
    
    # Run black
    console.print("Running black...")
    if not run_command("black staticflow tests"):
        console.print("[red]Black formatting failed[/red]")
        return False
        
    # Run isort
    console.print("Running isort...")
    if not run_command("isort staticflow tests"):
        console.print("[red]Import sorting failed[/red]")
        return False
        
    # Run mypy
    console.print("Running mypy...")
    if not run_command("mypy staticflow"):
        console.print("[red]Type checking failed[/red]")
        return False
        
    # Run flake8
    console.print("Running flake8...")
    if not run_command("flake8 staticflow tests"):
        console.print("[red]Linting failed[/red]")
        return False
        
    console.print("[green]Code quality checks passed![/green]")
    return True


def run_tests():
    """Run test suite."""
    console.print("\n[bold blue]Running tests...[/bold blue]")
    
    # Run pytest with coverage
    if not run_command("pytest tests/ --cov=staticflow --cov-report=term-missing"):
        console.print("[red]Tests failed[/red]")
        return False
        
    console.print("[green]All tests passed![/green]")
    return True


def build_documentation():
    """Build documentation."""
    console.print("\n[bold blue]Building documentation...[/bold blue]")
    
    docs_dir = Path("docs")
    if not docs_dir.exists():
        console.print("[red]Documentation directory not found[/red]")
        return False
        
    # Check documentation files
    required_docs = ["api.md", "user_guide.md"]
    for doc in required_docs:
        if not (docs_dir / doc).exists():
            console.print(f"[red]Missing documentation file: {doc}[/red]")
            return False
            
    console.print("[green]Documentation check passed![/green]")
    return True


def check_version():
    """Check version information."""
    console.print("\n[bold blue]Checking version information...[/bold blue]")
    
    # Check pyproject.toml
    if not Path("pyproject.toml").exists():
        console.print("[red]pyproject.toml not found[/red]")
        return False
        
    # Check version format
    import toml
    try:
        config = toml.load("pyproject.toml")
        version = config["tool"]["poetry"]["version"]
        if not version:
            console.print("[red]Version not set in pyproject.toml[/red]")
            return False
    except Exception as e:
        console.print(f"[red]Error reading version: {e}[/red]")
        return False
        
    console.print(f"[green]Version check passed: {version}[/green]")
    return True


def build_package():
    """Build Python package."""
    console.print("\n[bold blue]Building package...[/bold blue]")
    
    # Clean previous builds
    for path in Path(".").glob("dist/*"):
        path.unlink()
        
    # Build package
    if not run_command("poetry build"):
        console.print("[red]Package build failed[/red]")
        return False
        
    console.print("[green]Package built successfully![/green]")
    return True


def create_github_release():
    """Prepare GitHub release."""
    console.print("\n[bold blue]Preparing GitHub release...[/bold blue]")
    
    # Check git status
    if not run_command("git diff-index --quiet HEAD --"):
        console.print("[red]Working directory not clean[/red]")
        return False
        
    # Get version
    import toml
    version = toml.load("pyproject.toml")["tool"]["poetry"]["version"]
    
    # Create release notes template
    release_notes = Path("RELEASE_NOTES.md")
    if not release_notes.exists():
        release_notes.write_text(f"""# StaticFlow v{version}

## New Features
- 

## Improvements
- 

## Bug Fixes
- 

## Documentation
- 

## Breaking Changes
- 
""")
        console.print(f"[yellow]Created release notes template: {release_notes}[/yellow]")
        console.print("[yellow]Please fill in the release notes and run this script again[/yellow]")
        return False
        
    console.print("[green]GitHub release preparation complete![/green]")
    return True


def main():
    """Main release preparation function."""
    console.print(Panel.fit(
        "[bold yellow]StaticFlow Release Preparation[/bold yellow]\n\n"
        "This script will prepare StaticFlow for release by:\n"
        "1. Checking code quality\n"
        "2. Running tests\n"
        "3. Building documentation\n"
        "4. Checking version information\n"
        "5. Building package\n"
        "6. Preparing GitHub release"
    ))
    
    steps = [
        ("Code Quality", check_code_quality),
        ("Tests", run_tests),
        ("Documentation", build_documentation),
        ("Version", check_version),
        ("Package", build_package),
        ("GitHub Release", create_github_release)
    ]
    
    failed_steps = []
    
    for name, step in steps:
        console.print(f"\n[bold]Running step: {name}[/bold]")
        if not step():
            failed_steps.append(name)
            
    if failed_steps:
        console.print("\n[red]Release preparation failed![/red]")
        console.print("Failed steps:")
        for step in failed_steps:
            console.print(f"- {step}")
        sys.exit(1)
    else:
        console.print(Panel.fit(
            "[bold green]Release preparation complete![/bold green]\n\n"
            "Next steps:\n"
            "1. Review and commit any formatting changes\n"
            "2. Fill in the release notes\n"
            "3. Create a GitHub release\n"
            "4. Publish to PyPI using: poetry publish"
        ))


if __name__ == "__main__":
    main() 