import asyncio
import aiohttp
from aiohttp import web
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from rich.console import Console
from ..core.config import Config
from ..core.engine import Engine

console = Console()


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
        self.app = web.Application()
        self.setup_routes()
        self.setup_watchers()
        
    def setup_routes(self):
        """Setup server routes."""
        self.app.router.add_static('/static', Path('static'))
        self.app.router.add_static('/', Path('public'))
        self.app.router.add_get('/_dev/events', self.sse_handler)
        
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