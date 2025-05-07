from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from rich.console import Console
from rich.panel import Panel
from watchdog.events import FileSystemEventHandler
from ..core.engine import Engine
from ..admin import AdminPanel
from ..plugins import initialize_plugins
from ..utils.logging import get_logger

# Получаем логгер для данного модуля
logger = get_logger("core.server")

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


class Server:
    """StaticFlow server with optional development features."""
    
    def __init__(self, config, engine=None, host='localhost', port=8000, 
                 dev_mode=False):
        """
        Initialize the server.
        
        Args:
            config: Config instance
            engine: Engine instance, if not provided, a new one will be created
            host: Host to bind the server to
            port: Port to bind the server to
            dev_mode: Whether to enable development features
        """
        self.config = config
        self.host = host
        self.port = port
        self.dev_mode = dev_mode
        
        # Create engine if not provided
        if engine is None:
            self.engine = Engine(config)
        else:
            self.engine = engine
            
        # Initialize engine with directory paths
        source_dir = Path(self.config.get('source_dir', 'content'))
        output_dir = Path(self.config.get('output_dir', 'public'))
        template_dir = Path(self.config.get('template_dir', 'templates'))
        self.engine.initialize(source_dir, output_dir, template_dir)
        
        self.app = web.Application()
        self.admin = AdminPanel(config, self.engine)
        
        # Initialize plugins in dev mode
        if dev_mode:
            initialize_plugins(self.engine)
            
            # Validate project structure in dev mode
            errors, warnings = validate_project_structure()
            
            if errors:
                error_msg = "\n".join([
                    "Critical errors found:",
                    *[f"• {error}" for error in errors],
                    "\nPlease fix these issues before starting the server:",
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
                
            # Build the site in dev mode
            with console.status("[bold blue]Building site..."):
                try:
                    self.engine.build()
                    logger.info("Site built successfully!")
                except Exception as e:
                    error_msg = f"Error building site: {str(e)}"
                    logger.error(error_msg)
                    console.print(f"[red]{error_msg}[/red]")
                    raise SystemExit(1)
                
        # Setup routes and templates
        self.setup_routes()
        self.setup_templates()
            
    def setup_templates(self):
        """Setup Jinja2 templates."""
        template_dir = self.config.get('template_dir')
        
        # Convert to Path only if it's a string
        if not isinstance(template_dir, Path):
            template_path = Path(template_dir)
        else:
            template_path = template_dir
            
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(template_path))
        )
        
    def setup_routes(self):
        """Setup server routes."""
        # Admin routes
        self.app.router.add_get('/admin', self.admin_handler)
        self.app.router.add_get('/admin/{tail:.*}', self.admin_handler)
        self.app.router.add_post('/admin/api/{tail:.*}', self.admin_handler)
        self.app.router.add_post('/admin/{tail:.*}', self.admin_handler)
        
        # Static files
        static_url = self.config.get('static_url', '/static')
        static_dir = self.config.get('static_dir', 'static')
        if not isinstance(static_dir, Path):
            static_path = Path(static_dir)
        else:
            static_path = static_dir
        self.app.router.add_static(static_url, static_path)
        
        # All other routes
        self.app.router.add_get('/{tail:.*}', self.handle_request)
        
    async def admin_redirect(self, request):
        """Redirect /admin to /admin/."""
        return web.HTTPFound('/admin/')
        
    async def admin_handler(self, request):
        """Handle admin panel requests."""
        return await self.admin.handle_request(request)
        
    async def handle_request(self, request):
        """Handle regular site requests."""
        path = request.path
        
        # Default to index.html for root path
        if path == '/':
            path = '/index.html'
            
        output_dir = self.config.get('output_dir', 'public')
        # Convert to Path only if it's a string
        if not isinstance(output_dir, Path):
            output_path = Path(output_dir)
        else:
            output_path = output_dir
            
        # Ensure path is a string before calling lstrip
        if isinstance(path, Path):
            path = str(path)
            
        file_path = output_path / path.lstrip('/')
            
        if not file_path.exists():
            if self.dev_mode:
                return web.Response(status=404, text="Not Found")
            else:
                raise web.HTTPNotFound()
                
        if not file_path.is_file():
            return web.Response(status=403, text="Forbidden")
            
        # Set content type for common file extensions
        content_type = "text/html"
        if path.endswith(".css"):
            content_type = "text/css"
        elif path.endswith(".js"):
            content_type = "application/javascript"
            
        return web.FileResponse(
            file_path, 
            headers={"Content-Type": content_type}
        )
        
    def run(self):
        """Run the server."""
        if self.dev_mode:
            server_url = f"http://{self.host}:{self.port}"
            logger.info(f"Server running at {server_url}")
            console.print(
                Panel.fit(
                    f"[green]Server running at[/green] {server_url}\n"
                    "[dim]Press CTRL+C to stop[/dim]",
                    title="StaticFlow Dev Server"
                )
            )
            # Disable standard aiohttp output in dev mode
            web.run_app(
                self.app,
                host=self.host,
                port=self.port,
                print=None
            )
        else:
            server_url = f"http://{self.host}:{self.port}"
            logger.info(f"Production server running at {server_url}")
            web.run_app(self.app, host=self.host, port=self.port)


# Backwards compatibility for older code
class DevServer(Server):
    """Legacy class for backwards compatibility."""
    
    def __init__(self, config, host='localhost', port=8000):
        super().__init__(config, None, host, port, dev_mode=True)
        
    def start(self):
        """Start the development server (alias for run)."""
        self.run() 