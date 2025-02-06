from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..config import Config
from ..engine import Engine
from ..admin import AdminPanel


class Server:
    """Development server for StaticFlow."""
    
    def __init__(self, config: Config, engine: Engine):
        self.config = config
        self.engine = engine
        self.app = web.Application()
        self.admin = AdminPanel(config, engine)
        self.setup_routes()
        self.setup_templates()
        
    def setup_templates(self):
        """Setup Jinja2 templates."""
        template_path = Path(self.config.get('template_dir'))
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(template_path))
        )
        
    def setup_routes(self):
        """Setup server routes."""
        # Redirect /admin to /admin/
        self.app.router.add_get('/admin', self.admin_redirect)
        
        # Handle all /admin/ routes
        self.app.router.add_get('/admin/{tail:.*}', self.admin_handler)
        
        # Handle static files
        self.app.router.add_static(
            '/static',
            Path(self.config.get('static_dir'))
        )
        
        # Handle all other routes
        self.app.router.add_get('/{tail:.*}', self.handle_request)
        
    async def admin_redirect(self, request):
        """Redirect /admin to /admin/."""
        raise web.HTTPFound('/admin/')
        
    async def admin_handler(self, request):
        """Handle admin panel requests."""
        return await self.admin.handle_request(request)
        
    async def handle_request(self, request):
        """Handle regular site requests."""
        path = request.path
        if path == '/':
            path = '/index.html'
            
        file_path = Path('public') / path.lstrip('/')
        
        if not file_path.exists():
            raise web.HTTPNotFound()
            
        return web.FileResponse(file_path)
        
    def run(self, host: str = '127.0.0.1', port: int = 8000):
        """Run the development server."""
        web.run_app(self.app, host=host, port=port) 