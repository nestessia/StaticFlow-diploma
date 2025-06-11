from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from ..core.engine import Engine
from ..plugins import initialize_plugins
from ..utils.logging import get_logger

# Получаем логгер для данного модуля
logger = get_logger("core.builder")

console = Console()

REQUIRED_DIRECTORIES = ['content', 'templates', 'static']
REQUIRED_FILES = ['config.toml']


def validate_project_structure(config):
    """Validate project structure and permissions."""
    errors = []
    warnings = []

    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            errors.append(f"Directory '{dir_name}' not found")
        elif not dir_path.is_dir():
            errors.append(f"'{dir_name}' exists but is not a directory")
        else:
            try:
                test_file = dir_path / '.write_test'
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError):
                warnings.append(
                    f"Warning: Limited permissions on '{dir_name}' directory"
                )

    content_path = Path('content')
    if not content_path.exists() or not any(content_path.iterdir()):
        warnings.append("No content found in content directory")

    # Проверяем и создаём output_dir, если нужно
    output_dir = Path(config.get('output_dir'))
    if not output_dir.exists():
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Created output directory: {output_dir}")
        except Exception as e:
            errors.append(f"Could not create output directory '{output_dir}': {e}")
    elif not output_dir.is_dir():
        errors.append(f"'{output_dir}' exists but is not a directory")

    return errors, warnings


class Builder:
    """StaticFlow builder for generating static site."""

    def __init__(self, config, engine=None):
        """
        Initialize the builder.

        Args:
            config: Config instance
            engine: Engine instance, if not provided, a new one will be created
        """
        self.config = config

        if engine is None:
            self.engine = Engine(config)
        else:
            self.engine = engine

        source_dir = Path(self.config.get('source_dir', 'content'))
        output_dir = Path(self.config.get('output_dir'))
        template_dir = Path(self.config.get('template_dir', 'templates'))
        self.engine.initialize(source_dir, output_dir, template_dir)

        # Инициализируем плагины
        initialize_plugins(self.engine)

    def build(self):
        """Build the static site."""
        errors, warnings = validate_project_structure(self.config)

        if errors:
            error_msg = "\n".join([
                "Critical errors found:",
                *[f"• {error}" for error in errors],
                "\nPlease fix these issues before building:",
                "1. Make sure you're in the correct project directory",
                "2. Check if all required directories and files exist",
                "3. Verify file and directory permissions",
                "\nProject structure should be:",
                "project_name/",
                "├── content/",
                "├── templates/",
                "├── static/",
                f"├── {self.config.get('output_dir')}/",
                "└── config.toml"
            ])
            logger.error(error_msg)
            console.print(Panel(
                error_msg,
                title="[red]Project Structure Errors[/red]",
                border_style="red"
            ))
            raise SystemExit(1)

        if warnings:
            warning_msg = "\n".join([
                "Warnings:",
                *[f"• {warning}" for warning in warnings]
            ])
            logger.warning(warning_msg)
            console.print(Panel(
                warning_msg,
                title="[yellow]Project Structure Warnings[/yellow]",
                border_style="yellow"
            ))

        output_dir = Path(self.config.get('output_dir'))

        try:
            logger.info("Starting site build...")
            self.engine.build()
            logger.info("Site build completed successfully")
            console.print(
                Panel.fit(
                    "[green]Site build completed successfully[/green]\n"
                    f"Output directory: {output_dir}",
                    title="StaticFlow Builder"
                )
            )
        except Exception as e:
            error_msg = f"Error during site build: {str(e)}"
            logger.error(error_msg)
            console.print(
                Panel(
                    error_msg,
                    title="[red]Build Error[/red]",
                    border_style="red"
                )
            )
            raise
