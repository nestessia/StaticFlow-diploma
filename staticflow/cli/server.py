from aiohttp import web
from pathlib import Path
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from ..core.config import Config
from ..core.engine import Engine
from ..plugins import initialize_plugins

console = Console()

REQUIRED_DIRECTORIES = ['content', 'templates', 'static', 'public']
REQUIRED_FILES = ['config.toml']


def validate_project_structure():
    """Validate project structure and permissions."""
    errors = []
    warnings = []
    
    # Check required directories
    for dir_name in REQUIRED_DIRECTORIES:
        dir_path = Path(dir_name)
        if not dir_path.exists():
            errors.append(f"Directory '{dir_name}' not found")
        elif not dir_path.is_dir():
            errors.append(f"'{dir_name}' exists but is not a directory")
        else:
            try:
                # Try to create a temporary file to test write permissions
                test_file = dir_path / '.write_test'
                test_file.touch()
                test_file.unlink()
            except (PermissionError, OSError):
                warnings.append(
                    f"Warning: Limited permissions on '{dir_name}' directory"
                )
    
    # Check content structure
    content_path = Path('content')
    if not content_path.exists() or not any(content_path.iterdir()):
        warnings.append("No content found in content directory")
    
    return errors, warnings


class FileChangeHandler(FileSystemEventHandler):
    """Handler for file system changes."""
    
    def __init__(self, callback):
        self.callback = callback
        
    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)


class DevServer:
    """Development server with hot reload support."""
    
    def __init__(self, config: Config, host: str = 'localhost', port: int = 8000):
        self.config = config
        self.host = host
        self.port = port
        self.engine = Engine(config)
        
        # Initialize plugins
        initialize_plugins(self.engine)
        
        # Validate project structure before starting
        errors, warnings = validate_project_structure()
        
        if errors:
            console.print(Panel(
                "\n".join([
                    "[red]Critical errors found:[/red]",
                    *[f"• {error}" for error in errors],
                    "\n[yellow]Please fix these issues before starting the server:[/yellow]",
                    "1. Make sure you're in the correct project directory",
                    "2. Check if all required directories and files exist",
                    "3. Verify file and directory permissions",
                    "\nProject structure should be:",
                    "project_name/",
                    "├── content/",
                    "├── templates/",
                    "├── static/",
                    "├── public/",
                    "└── config.toml"
                ]),
                title="[red]Project Structure Errors[/red]",
                border_style="red"
            ))
            raise SystemExit(1)
        
        if warnings:
            console.print(Panel(
                "\n".join([
                    "[yellow]Warnings:[/yellow]",
                    *[f"• {warning}" for warning in warnings]
                ]),
                title="[yellow]Project Structure Warnings[/yellow]",
                border_style="yellow"
            ))
            
        # Build the site before starting server
        with console.status("[bold blue]Building site..."):
            try:
                self.engine.build()
                console.print("[green]Site built successfully![/green]")
            except Exception as e:
                console.print(f"[red]Error building site:[/red] {str(e)}")
                raise SystemExit(1)
            
    async def handle_request(self, request):
        """Handle incoming HTTP request."""
        path = request.path
        
        # Serve files from public directory
        if path == "/":
            path = "/index.html"
            
        file_path = Path(self.config.get("output_dir")) / path.lstrip("/")
        
        if not file_path.exists():
            return web.Response(status=404, text="Not Found")
            
        if not file_path.is_file():
            return web.Response(status=403, text="Forbidden")
            
        content_type = "text/html"
        if path.endswith(".css"):
            content_type = "text/css"
        elif path.endswith(".js"):
            content_type = "application/javascript"
            
        return web.FileResponse(file_path, headers={"Content-Type": content_type})
        
    def start(self):
        """Start the development server."""
        app = web.Application()
        app.router.add_get('/{tail:.*}', self.handle_request)
        
        web.run_app(app, host=self.host, port=self.port) 