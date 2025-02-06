from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..core.config import Config
from ..core.engine import Engine


class AdminPanel:
    """Admin panel for StaticFlow."""
    
    def __init__(self, config: Config, engine: Engine):
        self.config = config
        self.engine = engine
        self.app = web.Application()
        self.setup_routes()
        self.setup_templates()
        
    def setup_templates(self):
        """Setup Jinja2 templates for admin panel."""
        template_path = Path(__file__).parent / 'templates'
        print(f"Template path: {template_path} (exists: {template_path.exists()})")
        
        if not template_path.exists():
            template_path.mkdir(parents=True)
            print(f"Created template directory: {template_path}")
            
        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader(str(template_path))
        )
        
    def setup_routes(self):
        """Setup admin panel routes."""
        self.app.router.add_get('', self.index_handler)
        self.app.router.add_get('/', self.index_handler)  # Добавляем явный обработчик для /
        self.app.router.add_get('/content', self.content_handler)
        self.app.router.add_get('/settings', self.settings_handler)
        self.app.router.add_post('/api/content', self.api_content_handler)
        self.app.router.add_post('/api/settings', self.api_settings_handler)
        
        # Добавляем статические файлы
        static_path = Path(__file__).parent / 'static'
        print(f"Static path: {static_path} (exists: {static_path.exists()})")
        
        if not static_path.exists():
            static_path.mkdir(parents=True)
            print(f"Created static directory: {static_path}")
            
        self.app.router.add_static('/static', static_path)
        
    async def handle_request(self, request):
        """Handle admin panel request."""
        print(f"Admin request: {request.path}")
        
        # Remove /admin prefix from path
        path = request.path.replace('/admin', '', 1)
        if not path:
            path = '/'
            
        print(f"Modified path: {path}")
        
        # Create subrequest with modified path
        subrequest = request.clone(rel_url=path)
        
        try:
            # Handle the request using the admin app
            response = await self.app._handle(subrequest)
            return response
        except web.HTTPNotFound:
            print(f"Admin page not found: {path}")
            return web.Response(status=404, text="Admin page not found")
        except Exception as e:
            print(f"Error handling admin request: {e}")
            return web.Response(status=500, text=str(e))
        
    @aiohttp_jinja2.template('index.html')
    async def index_handler(self, request):
        """Handle admin panel index page."""
        return {
            'site_name': self.config.get('site_name'),
            'content_count': len(list(Path('content').rglob('*.*'))),
            'last_build': 'Not built yet'  # TODO: Add build timestamp
        }
        
    @aiohttp_jinja2.template('content.html')
    async def content_handler(self, request):
        """Handle content management page."""
        content_path = Path('content')
        files = []
        
        for file in content_path.rglob('*.*'):
            if file.suffix in ['.md', '.html']:
                files.append({
                    'path': str(file.relative_to(content_path)),
                    'modified': file.stat().st_mtime,
                    'size': file.stat().st_size
                })
                
        return {
            'files': files
        }
        
    @aiohttp_jinja2.template('settings.html')
    async def settings_handler(self, request):
        """Handle settings page."""
        return {
            'config': self.config.config
        }
        
    async def api_content_handler(self, request):
        """Handle content API requests."""
        data = await request.json()
        action = data.get('action')
        
        if not action:
            return web.json_response({
                'status': 'error',
                'message': 'Missing action field'
            })
            
        if action not in ['create', 'update', 'delete']:
            return web.json_response({
                'status': 'error',
                'message': 'Invalid action'
            })
            
        if 'path' not in data:
            return web.json_response({
                'status': 'error',
                'message': 'Missing path field'
            })
        
        if action == 'create':
            # Create new content file
            path = Path('content') / data['path']
            path.write_text(data['content'], encoding='utf-8')
            await self.rebuild_site()
            return web.json_response({'status': 'ok'})
            
        elif action == 'update':
            # Update existing content file
            path = Path('content') / data['path']
            path.write_text(data['content'], encoding='utf-8')
            await self.rebuild_site()
            return web.json_response({'status': 'ok'})
            
        elif action == 'delete':
            # Delete content file
            path = Path('content') / data['path']
            path.unlink()
            await self.rebuild_site()
            return web.json_response({'status': 'ok'})
            
        return web.json_response({
            'status': 'error',
            'message': 'Invalid action'
        })
        
    async def api_settings_handler(self, request):
        """Handle settings API requests."""
        data = await request.json()
        
        # Update config
        for key, value in data.items():
            self.config.set(key, value)
            
        # Save config
        with open('config.toml', 'w', encoding='utf-8') as f:
            import toml
            toml.dump(self.config.config, f)
            
        await self.rebuild_site()
        return web.json_response({'status': 'ok'})
        
    async def rebuild_site(self):
        """Rebuild the site after changes."""
        try:
            self.engine.build()
            return True
        except Exception as e:
            print(f"Error rebuilding site: {e}")
            return False
            
    def start(self, host: str = 'localhost', port: int = 8001):
        """Start the admin panel server."""
        web.run_app(self.app, host=host, port=port) 