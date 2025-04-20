from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..core.config import Config
from ..core.engine import Engine
import json
import shutil
from datetime import datetime
import re
from ..utils.logging import get_logger

# Получаем логгер для данного модуля
logger = get_logger("admin")


class AdminPanel:
    """Admin panel for StaticFlow."""
    
    def __init__(self, config: Config, engine: Engine):
        self.config = config
        self.engine = engine
        self.app = web.Application()
        self.setup_routes()
        self.setup_templates()
        
    def _safe_metadata(self, metadata):
        """Convert metadata to JSON-safe format."""
        if not metadata:
            return {}
            
        result = {}
        for key, value in metadata.items():
            if key == 'date' and hasattr(value, 'isoformat'):
                # Convert datetime to ISO string
                result[key] = value.isoformat()
            elif isinstance(value, (str, int, float, bool, type(None))):
                # These types are JSON-serializable
                result[key] = value
            elif isinstance(value, list):
                # Handle lists (e.g., tags)
                safe_list = []
                for item in value:
                    if isinstance(item, (str, int, float, bool)):
                        safe_list.append(item)
                    else:
                        safe_list.append(str(item))
                result[key] = safe_list
            else:
                # Convert other types to string
                result[key] = str(value)
                
        return result
        
    def setup_templates(self):
        """Setup Jinja2 templates for admin panel."""
        template_path = Path(__file__).parent / 'templates'
        
        if not template_path.exists():
            template_path.mkdir(parents=True)
            logger.info(f"Created template directory: {template_path}")
            
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
        
        # Добавляем маршруты для блочного редактора
        self.app.router.add_get('/block-editor', self.block_editor_handler)
        self.app.router.add_get('/block-editor/{path:.*}', self.block_editor_handler)
        self.app.router.add_post('/api/preview', self.api_preview_handler)
        
        # Добавляем маршруты для деплоя на GitHub Pages
        self.app.router.add_get('/deploy', self.deploy_handler)
        self.app.router.add_get('/api/deploy/config', self.api_deploy_config_get_handler)  # GET для получения свежих данных
        self.app.router.add_post('/api/deploy/config', self.api_deploy_config_handler)
        self.app.router.add_post('/api/deploy/start', self.api_deploy_start_handler)
        
        # Добавляем статические файлы
        static_path = Path(__file__).parent / 'static'
        
        if not static_path.exists():
            static_path.mkdir(parents=True)
        
        # Проверяем наличие кэшированной статики в public
        cached_static_path = Path('public/admin/static')
        use_cached = cached_static_path.exists()
        
        # Используем кэшированную статику, если она есть, иначе берем из фреймворка
        final_static_path = cached_static_path if use_cached else static_path
        self.app.router.add_static('/static', final_static_path)
        
        # Если кэш не существует, копируем статику при инициализации
        if not use_cached:
            self.copy_static_to_public()
        
    async def handle_request(self, request):
        """Handle admin panel request."""
        logger.info(f"Admin request: {request.path}, method: {request.method}")
        
        # Remove /admin prefix from path
        path = request.path.replace('/admin', '', 1)
        if not path:
            path = '/'
            
        logger.info(f"Modified path: {path}")
        
        # Прямое перенаправление для API запросов без клонирования
        if path.startswith('/api/'):
            # GET запросы к API
            if request.method == 'GET':
                if path == '/api/deploy/config':
                    return await self.api_deploy_config_get_handler(request)
            
            # POST запросы к API
            if request.method == 'POST':
                # Маршрутизация API напрямую к обработчикам
                if path == '/api/content':
                    return await self.api_content_handler(request)
                elif path == '/api/preview':
                    return await self.api_preview_handler(request)
                elif path == '/api/settings':
                    return await self.api_settings_handler(request)
                elif path == '/api/deploy/config':
                    return await self.api_deploy_config_handler(request)
                elif path == '/api/deploy/start':
                    return await self.api_deploy_start_handler(request)
                else:
                    return web.json_response({
                        'success': False,
                        'error': f"Unknown API endpoint: {path}"
                    }, status=404)
        
        # Для GET запросов и всех остальных используем клонирование
        try:
            # Клонируем запрос с новым URL
            subrequest = request.clone(rel_url=path)
            
            # Обрабатываем запрос через приложение админ-панели
            response = await self.app._handle(subrequest)
            return response
        except web.HTTPNotFound:
            logger.info(f"Admin page not found: {path}")
            return web.Response(status=404, text="Admin page not found")
        except Exception as e:
            logger.error(f"Error handling admin request: {e}")
            import traceback
            traceback.print_exc()
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
        
    @aiohttp_jinja2.template('deploy.html')
    async def deploy_handler(self, request):
        """Handle deployment page."""
        # Инициализируем GitHub Pages deployer
        from ..deploy.github_pages import GitHubPagesDeployer
        deployer = GitHubPagesDeployer()
        
        # Получаем статус и конфигурацию деплоя
        status = deployer.get_deployment_status()
        
        return {
            'status': status,
            'config': status['config']
        }
        
    @aiohttp_jinja2.template('block_editor.html')
    async def block_editor_handler(self, request):
        """Handle block editor page."""
        path = request.match_info.get('path', '')
        page = None
        safe_metadata = {}
        
        if path:
            content_path = Path('content') / path
            logger.info(f"Attempting to load page from: {content_path}")
            if content_path.exists():
                try:
                    # Создаем объект Page из существующего файла
                    from ..core.page import Page
                    page = Page.from_file(content_path)
                    
                    # Устанавливаем правильный путь к исходному файлу
                    page.source_path = path
                    
                    # Добавляем время последнего изменения файла, если его нет
                    if not hasattr(page, 'modified'):
                        page.modified = content_path.stat().st_mtime
                    # Преобразуем метаданные в JSON-безопасный формат
                    safe_metadata = self._safe_metadata(page.metadata)
                    logger.info(f"Successfully loaded page: {path}")
                
                except Exception as e:
                    logger.error(f"Error loading page: {e}")
                    import traceback
                    traceback.print_exc()
        
        return {
            'page': page,
            'safe_metadata': safe_metadata
        }
    
    async def api_content_handler(self, request):
        """Handle content API requests."""
        try:
            data = await request.json()
            
            if 'path' not in data:
                return web.json_response({
                    'success': False,
                    'error': 'Missing path field'
                }, status=400)
                
            if 'content' not in data:
                return web.json_response({
                    'success': False,
                    'error': 'Missing content field'
                }, status=400)
                
            path = data['path']
            content = data['content']
            metadata = data.get('metadata', {})
            
            # Handle new page creation
            is_new_page = path == 'New Page'
            if is_new_page:
                title = metadata.get('title', 'Untitled')
                # Create sanitized filename from title
                filename = title.lower().replace(' ', '-')
                # Remove any character that's not alphanumeric, dash, or underscore
                filename = re.sub(r'[^a-z0-9\-_]', '', filename)
                # Ensure we have a valid filename
                if not filename:
                    filename = 'untitled'
                
                # Set path to new file in content directory
                path = f"{filename}.md"
                logger.info(f"Creating new page at: {path}")
            
            # Normalize path to be relative to content directory
            if path.startswith('/'):
                path = path[1:]
                
            content_path = Path('content') / path
            
            # Ensure parent directories exist
            content_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Create frontmatter
            frontmatter = '---\n'
            for key, value in metadata.items():
                if isinstance(value, list):
                    frontmatter += f"{key}:\n"
                    for item in value:
                        frontmatter += f"  - {item}\n"
                else:
                    frontmatter += f"{key}: {value}\n"
            frontmatter += '---\n\n'
            
            # Write content to file with frontmatter
            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)
                
            # Rebuild the site
            self.rebuild_site()
            
            return web.json_response({
                'success': True,
                'path': path
            })
            
        except json.JSONDecodeError as e:
            logger.error(f"Content JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in api_content_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
        
    async def api_preview_handler(self, request):
        """Handle preview API requests."""
        try:
            data = await request.json()
            
            if 'content' not in data:
                return web.Response(
                    status=400,
                    text="Missing content field"
                )
                
            content = data['content']
            metadata = data.get('metadata', {})
            
            # Рендерим контент напрямую с помощью стандартной библиотеки markdown
            import markdown
            import re
            
            # Предварительная обработка математических формул
            def process_math(text):
                # Обработка inline формул
                text = re.sub(r'\$(.+?)\$', r'<span class="math">\1</span>', text)
                # Обработка block формул
                text = re.sub(r'\$\$(.*?)\$\$', r'<div class="math math-display">\1</div>', text, flags=re.DOTALL)
                return text
            
            # Предварительная обработка специальных блоков
            def process_special_blocks(text):
                # Обработка информационных блоков
                text = re.sub(r':::info(.*?):::', r'<div class="info">\1</div>', text, flags=re.DOTALL)
                text = re.sub(r':::warning(.*?):::', r'<div class="warning">\1</div>', text, flags=re.DOTALL)
                text = re.sub(r':::danger(.*?):::', r'<div class="danger">\1</div>', text, flags=re.DOTALL)
                return text

            # Предварительная обработка контента
            content = process_math(content)
            content = process_special_blocks(content)
            
            # Создаем экземпляр Markdown с расширенными возможностями
            md = markdown.Markdown(extensions=[
                'fenced_code',
                'tables',
                'codehilite',
                'toc',
                'attr_list',
                'def_list',
                'footnotes',
                'nl2br'
            ])
            
            # Рендерим контент
            html_content = md.convert(content)
            
            # Оборачиваем HTML в базовый шаблон для предпросмотра
            preview_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <title>{metadata.get('title', 'Preview')}</title>
                <!-- KaTeX для математических формул -->
                <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.css">
                <script src="https://cdn.jsdelivr.net/npm/katex@0.16.8/dist/katex.min.js"></script>
                <!-- Mermaid для диаграмм -->
                <script src="https://cdn.jsdelivr.net/npm/mermaid@10.2.3/dist/mermaid.min.js"></script>
                <!-- Подсветка синтаксиса -->
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/styles/github.min.css">
                <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js"></script>
                <style>
                    body {{ 
                        font-family: system-ui, sans-serif; 
                        line-height: 1.6; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px;
                        color: #333;
                    }}
                    h1, h2, h3, h4, h5, h6 {{ 
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    h1 {{ font-size: 2em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    h2 {{ font-size: 1.5em; border-bottom: 1px solid #eaecef; padding-bottom: 0.3em; }}
                    h3 {{ font-size: 1.25em; }}
                    a {{ color: #0366d6; text-decoration: none; }}
                    a:hover {{ text-decoration: underline; }}
                    pre {{ 
                        background: #f6f8fa; 
                        padding: 16px; 
                        border-radius: 6px; 
                        overflow: auto;
                        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                        font-size: 85%;
                        line-height: 1.45;
                        margin: 1em 0;
                    }}
                    code {{ 
                        background: rgba(27, 31, 35, 0.05);
                        border-radius: 3px;
                        font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace;
                        font-size: 85%;
                        margin: 0;
                        padding: 0.2em 0.4em;
                    }}
                    pre code {{ 
                        background: transparent;
                        padding: 0;
                        margin: 0;
                        font-size: 100%;
                        word-break: normal;
                        white-space: pre;
                        border: 0;
                    }}
                    blockquote {{ 
                        border-left: 4px solid #ddd; 
                        padding-left: 1em; 
                        color: #6a737d;
                        margin: 1em 0;
                    }}
                    img {{ max-width: 100%; }}
                    table {{
                        border-collapse: collapse;
                        margin: 1em 0;
                        overflow: auto;
                        width: 100%;
                    }}
                    table th, table td {{
                        border: 1px solid #dfe2e5;
                        padding: 6px 13px;
                    }}
                    table tr {{
                        background-color: #fff;
                        border-top: 1px solid #c6cbd1;
                    }}
                    table tr:nth-child(2n) {{
                        background-color: #f6f8fa;
                    }}
                    /* Стили для Mermaid диаграмм */
                    .mermaid {{ 
                        text-align: center;
                        margin: 1.5em 0;
                        background: transparent;
                    }}
                    /* Стили для математических формул */
                    .math {{ 
                        overflow-x: auto;
                        margin: 1em 0;
                        background: transparent;
                    }}
                    .math-display {{
                        display: block;
                        text-align: center;
                        margin: 1em 0;
                    }}
                    /* Стили для информационных блоков */
                    .info, .warning, .danger {{
                        padding: 1em;
                        margin: 1em 0;
                        border-radius: 4px;
                    }}
                    .info {{
                        background-color: #f0f7ff;
                        border: 1px solid #bae3ff;
                    }}
                    .warning {{
                        background-color: #fffbf0;
                        border: 1px solid #ffe7a3;
                    }}
                    .danger {{
                        background-color: #fff0f0;
                        border: 1px solid #ffbaba;
                    }}
                </style>
            </head>
            <body>
                <h1>{metadata.get('title', 'Preview')}</h1>
                {html_content}
                <script>
                    // Инициализация Mermaid
                    mermaid.initialize({{startOnLoad: true}});
                    
                    // Инициализация подсветки кода
                    document.querySelectorAll('pre code').forEach((block) => {{
                        hljs.highlightBlock(block);
                    }});
                    
                    // Инициализация KaTeX
                    document.querySelectorAll('.math').forEach(function(element) {{
                        try {{
                            katex.render(element.textContent, element, {{
                                throwOnError: false,
                                displayMode: element.classList.contains('math-display')
                            }});
                        }} catch (e) {{
                            console.error('KaTeX error:', e);
                        }}
                    }});
                </script>
            </body>
            </html>
            """
            
            return web.Response(
                text=preview_html,
                content_type='text/html'
            )
        except json.JSONDecodeError as e:
            logger.error(f"Preview JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in api_preview_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
        
    async def api_settings_handler(self, request):
        """Handle settings API requests."""
        try:
            data = await request.json()
            
            for key, value in data.items():
                self.config.set(key, value)
                
            self.config.save()
            self.rebuild_site()
            
            return web.json_response({'status': 'ok'})
        except json.JSONDecodeError as e:
            logger.error(f"Settings JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in api_settings_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
            
    async def api_deploy_config_get_handler(self, request):
        """Handle deploy configuration GET API requests."""
        try:
            # Инициализируем GitHub Pages deployer
            from ..deploy.github_pages import GitHubPagesDeployer
            deployer = GitHubPagesDeployer()
            
            # Получаем статус и конфигурацию деплоя
            status = deployer.get_deployment_status()
            
            return web.json_response({
                'success': True,
                'status': status,
                'config': status['config']
            })
        except Exception as e:
            logger.error(f"Error in api_deploy_config_get_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
            
    async def api_deploy_config_handler(self, request):
        """Handle deploy configuration API requests."""
        try:
            data = await request.json()
            
            # Инициализируем GitHub Pages deployer
            from ..deploy.github_pages import GitHubPagesDeployer
            deployer = GitHubPagesDeployer()
            
            # Обновляем конфигурацию
            deployer.update_config(**data)
            
            # Проверяем, валидна ли конфигурация
            is_valid, errors, warnings = deployer.validate_config()
            
            return web.json_response({
                'success': True,
                'is_valid': is_valid,
                'errors': errors if not is_valid else [],
                'warnings': warnings
            })
        except json.JSONDecodeError as e:
            logger.error(f"Deploy config JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            logger.error(f"Unexpected error in api_deploy_config_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e),
                'message': 'Failed to save deployment configuration'
            }, status=500)
            
    async def api_deploy_start_handler(self, request):
        """Handle deploy start API requests."""
        logger.info("=== Starting deployment process ===")
        try:
            # Получаем данные из запроса
            data = {}
            try:
                data = await request.json()
                logger.info(f"Received deployment data: {data}")
            except json.JSONDecodeError:
                # Если JSON не предоставлен, используем пустой словарь
                logger.info("No JSON data provided in request")
                pass
                
            # Получаем коммит-сообщение, если предоставлено
            commit_message = data.get('commit_message')
            logger.info(f"Using commit message: {commit_message or 'default'}")
            
            # Инициализируем GitHub Pages deployer
            from ..deploy.github_pages import GitHubPagesDeployer
            logger.info("Initializing GitHubPagesDeployer")
            deployer = GitHubPagesDeployer()
            
            # Проверяем, валидна ли конфигурация
            logger.info("Validating deployment configuration")
            is_valid, errors, warnings = deployer.validate_config()
            if not is_valid:
                logger.error(f"Invalid configuration: {errors}")
                return web.json_response({
                    'success': False,
                    'message': f"Invalid configuration: {', '.join(errors)}"
                }, status=400)
                
            # Сначала перестраиваем сайт
            logger.info("Rebuilding site before deployment")
            rebuild_success = self.rebuild_site()
            if not rebuild_success:
                logger.error("Failed to build site")
                return web.json_response({
                    'success': False,
                    'message': 'Failed to build site'
                }, status=500)
            
            logger.info("Site successfully rebuilt, starting deployment")
                
            # Деплоим сайт
            logger.info(f"Deploying site with committer: {deployer.config.get('username')}")
            success, message = deployer.deploy(commit_message=commit_message)
            logger.info(f"Deployment result: success={success}, message={message}")
            
            # Получаем обновленный статус
            status = deployer.get_deployment_status()
            
            logger.info("=== Deployment process completed ===")
            return web.json_response({
                'success': success,
                'message': message,
                'timestamp': status.get('last_deployment'),
                'history': status.get('history', []),
                'warnings': warnings
            })
        except Exception as e:
            logger.error(f"Critical error in api_deploy_start_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'message': f"Deployment failed: {str(e)}"
            }, status=500)
        
    def copy_static_to_public(self):
        """Копирует статические файлы админки в папку public для кэширования."""
        source_static_path = Path(__file__).parent / 'static'
        if not source_static_path.exists():
            logger.info("Исходная директория статики не существует, нечего копировать")
            return
            
        dest_static_path = Path('public/admin/static')
        
        # Создаем директории, если они не существуют
        dest_static_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Копируем статические файлы
        if dest_static_path.exists():
            shutil.rmtree(dest_static_path)
        shutil.copytree(source_static_path, dest_static_path)
    
    def rebuild_site(self):
        """Rebuild the site using the engine."""
        try:
            # Убедимся, что статика админки тоже обновлена
            self.copy_static_to_public()
            
            self.engine.build()
            return True
        except Exception as e:
            logger.error(f"Error rebuilding site: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def start(self, host: str = 'localhost', port: int = 8001):
        """Start the admin panel server."""
        web.run_app(self.app, host=host, port=port)

# Экспортируем AdminPanel для доступа из других модулей
__all__ = ['AdminPanel'] 