import asyncio
from aiohttp import web
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from rich.panel import Panel
from ..core.config import Config
from ..core.engine import Engine

console = Console()

REQUIRED_DIRECTORIES = ['content', 'templates', 'static', 'public']
REQUIRED_FILES = ['config.toml']


def create_welcome_page():
    """Create welcome page and necessary files for new projects."""
    content_dir = Path('content/pages')
    templates_dir = Path('templates')
    static_dir = Path('static/css')
    
    # Create directories if they don't exist
    content_dir.mkdir(parents=True, exist_ok=True)
    templates_dir.mkdir(parents=True, exist_ok=True)
    static_dir.mkdir(parents=True, exist_ok=True)
    
    # Create welcome page
    welcome_content = """---
title: Welcome to StaticFlow
template: base.html
---
<div class="welcome-container">
    <h1 class="welcome-title">Welcome to StaticFlow!</h1>
    
    <div class="welcome-content">
        <p>
            Congratulations! Your StaticFlow site is up and running. 
            Now you can start creating your content.
        </p>
        
        <h2>Getting Started</h2>
        <ol class="steps-list">
            <li>Create content in <code>content/pages/</code> using Markdown or HTML</li>
            <li>Customize templates in <code>templates/</code> directory</li>
            <li>Add your styles to <code>static/css/</code> directory</li>
            <li>Configure your site in <code>config.toml</code></li>
        </ol>
        
        <h2>Example Structure</h2>
        <pre class="file-tree">
project_name/
├── content/
│   └── pages/
│       ├── index.md
│       └── about.md
├── templates/
│   └── base.html
├── static/
│   └── css/
│       └── style.css
├── public/
└── config.toml</pre>
        
        <div class="help-section">
            <h2>Need Help?</h2>
            <p>
                Check out our documentation or visit our GitHub repository 
                for more information.
            </p>
        </div>
    </div>
</div>"""

    # Create base template
    base_template = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ page.title }}</title>
    <link rel="stylesheet" href="/static/css/style.css">
</head>
<body>
    <main>
        {{ page.content }}
    </main>
</body>
</html>"""

    # Create basic styles
    welcome_styles = """/* Welcome page styles */
body {
    font-family: system-ui, -apple-system, sans-serif;
    line-height: 1.5;
    margin: 0;
    padding: 20px;
    background: #f5f5f5;
}

.welcome-container {
    max-width: 800px;
    margin: 0 auto;
    background: white;
    padding: 2rem;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.welcome-title {
    color: #2563eb;
    font-size: 2.5rem;
    text-align: center;
    margin-bottom: 2rem;
}

.welcome-content {
    color: #374151;
}

.steps-list {
    padding-left: 1.5rem;
}

.steps-list li {
    margin-bottom: 0.5rem;
}

code {
    background: #f1f5f9;
    padding: 0.2rem 0.4rem;
    border-radius: 4px;
    font-family: monospace;
}

.file-tree {
    background: #f8fafc;
    padding: 1rem;
    border-radius: 4px;
    font-family: monospace;
    white-space: pre;
    overflow-x: auto;
}

.help-section {
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid #e5e7eb;
}"""

    # Write files
    index_path = content_dir / 'index.md'
    template_path = templates_dir / 'base.html'
    style_path = static_dir / 'style.css'
    
    index_path.write_text(welcome_content)
    template_path.write_text(base_template)
    style_path.write_text(welcome_styles)


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
    content_path = Path('content/pages')
    if not content_path.exists() or not any(content_path.iterdir()):
        warnings.append("No content found - creating welcome page")
        try:
            create_welcome_page()
        except Exception as e:
            warnings.append(f"Failed to create welcome page: {str(e)}")
    
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
                    "│   └── pages/",
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
        
        # Ensure output directory exists
        self.output_dir = Path('public')
        self.output_dir.mkdir(exist_ok=True)
        
        self.app = web.Application()
        self.setup_routes()
        self.setup_watchers()
        
    def setup_routes(self):
        """Setup server routes."""
        try:
            self.app.router.add_static('/static', Path('static'))
            self.app.router.add_static('/', self.output_dir)
            self.app.router.add_get('/_dev/events', self.sse_handler)
        except Exception as e:
            console.print(Panel(
                "\n".join([
                    f"[red]Error setting up routes:[/red]\n{str(e)}\n",
                    "Common solutions:",
                    "1. Check if 'static' and 'public' directories exist",
                    "2. Verify directory permissions",
                    "3. Make sure you're in the project root directory"
                ]),
                title="[red]Server Configuration Error[/red]",
                border_style="red"
            ))
            raise
        
    def setup_watchers(self):
        """Setup file system watchers."""
        self.observer = Observer()
        handler = FileChangeHandler(self.handle_file_change)
        
        # Watch content and templates directories
        self.observer.schedule(handler, 'content', recursive=True)
        self.observer.schedule(handler, 'templates', recursive=True)
        self.observer.schedule(handler, 'static', recursive=True)
        
    async def sse_handler(self, request):
        """Server-Sent Events handler for live reload."""
        response = web.StreamResponse(
            status=200,
            reason='OK',
            headers={
                'Content-Type': 'text/event-stream',
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
            }
        )
        
        await response.prepare(request)
        
        while True:
            await response.write(b'data: ping\n\n')
            await asyncio.sleep(1)
            
    def handle_file_change(self, path: str):
        """Handle file system changes."""
        try:
            console.print(f"[yellow]File changed:[/yellow] {path}")
            self.engine.build()
            console.print("[green]Site rebuilt successfully![/green]")
        except Exception as e:
            console.print(f"[red]Error rebuilding site:[/red] {str(e)}")
            
    def inject_live_reload(self):
        """Inject live reload script into HTML files."""
        script = """
        <script>
            const evtSource = new EventSource('/_dev/events');
            evtSource.onmessage = function(event) {
                if (event.data === 'reload') {
                    window.location.reload();
                }
            }
        </script>
        """
        
        public_dir = Path('public')
        for html_file in public_dir.rglob('*.html'):
            content = html_file.read_text(encoding='utf-8')
            if '</body>' in content and script not in content:
                content = content.replace('</body>', f'{script}</body>')
                html_file.write_text(content, encoding='utf-8')
                
    def start(self):
        """Start the development server."""
        try:
            self.observer.start()
            self.inject_live_reload()
            web.run_app(self.app, host=self.host, port=self.port)
        finally:
            self.observer.stop()
            self.observer.join() 