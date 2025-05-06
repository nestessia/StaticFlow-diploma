from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..core.config import Config
from ..core.engine import Engine
import json
import logging
import os
import re
import secrets
import shutil
import time
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
        """Setup Jinja2 templates for admin panel and site preview (project-aware)."""
        from pathlib import Path
        # Получаем путь к шаблонам из пользовательского конфига
        template_dir = self.config.get('template_dir', 'templates')
        if not isinstance(template_dir, Path):
            template_path = Path(template_dir)
        else:
            template_path = template_dir
        admin_template_path = Path(__file__).parent / 'templates'

        if not admin_template_path.exists():
            admin_template_path.mkdir(parents=True)
            logger.info(f"Created template directory: {admin_template_path}")

        aiohttp_jinja2.setup(
            self.app,
            loader=jinja2.FileSystemLoader([
                str(admin_template_path),
                str(template_path)
            ])
        )
        
    def setup_routes(self):
        """Setup admin panel routes."""
        self.app.router.add_get('', self.index_handler)
        self.app.router.add_get('/', self.index_handler)  # Добавляем явный обработчик для /
        self.app.router.add_get('/content', self.index_handler)  # Переиспользуем index_handler для /content
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
        
    @aiohttp_jinja2.template('content.html')
    async def index_handler(self, request):
        """Handle admin panel index page."""
        # Вместо перенаправления сразу возвращаем содержимое страницы content
        content_path = Path('content')
        files = []
        
        # Используем конфигурацию из engine для определения URL файлов
        engine = self.engine
        site = engine.site
        base_url = self.config.get('base_url', '')
        
        for file in content_path.rglob('*.*'):
            if file.suffix in ['.md', '.html']:
                rel_path = str(file.relative_to(content_path))
                
                # Получаем URL для файла
                file_url = ""
                try:
                    # Загружаем страницу для получения ее метаданных
                    page = engine.load_page_from_file(file)
                    if page:
                        # Получаем тип контента
                        content_type = site.determine_content_type(page)
                        
                        # Формируем URL
                        file_url = site.router.get_url(content_type, page.metadata)
                        
                        # Добавляем base_url
                        if file_url and not file_url.startswith('http'):
                            if not file_url.startswith('/'):
                                file_url = '/' + file_url
                            file_url = f"{base_url.rstrip('/')}{file_url}"
                except Exception as e:
                    logger.error(f"Error generating URL for {rel_path}: {e}")
                
                # Если не удалось получить URL, используем преобразование пути
                if not file_url:
                    file_url = f"{base_url.rstrip('/')}/{rel_path.replace('.md', '.html')}"
                
                # Добавляем информацию о файле
                files.append({
                    'path': rel_path,
                    'modified': file.stat().st_mtime,
                    'size': file.stat().st_size,
                    'url': file_url
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
    
    @aiohttp_jinja2.template('default/page.html')
    async def api_preview_handler(self, request):
        """Handle preview API requests (site-like preview)."""
        try:
            data = await request.json()
            if 'content' not in data:
                return web.Response(status=400, text="Missing content field")
            content = data['content']
            metadata = data.get('metadata', {})
            # Формируем временный page-объект для шаблона
            page = {
                'title': metadata.get('title', 'Preview'),
                'content': content,
                'head_content': '',  # Можно добавить генерацию head, если нужно
                'metadata': metadata
            }
            return {'page': page}
        except Exception as e:
            import traceback
            traceback.print_exc()
            return web.Response(status=500, text=str(e))
        
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
                # Проверяем, если путь новой страницы уже содержит имя файла
                if '.' in path and path != 'New Page':
                    # Используем путь как есть
                    logger.info(f"Using provided path for new page: {path}")
                else:
                    # Используем имя файла из заголовка, если не указано явно
                    title = metadata.get('title', 'Untitled')
                    # Create sanitized filename from title
                    filename = title.lower().replace(' ', '-')
                    # Remove any character that's not alphanumeric, dash, or underscore
                    filename = re.sub(r'[^a-z0-9\-_]', '', filename)
                    # Ensure we have a valid filename
                    if not filename:
                        filename = 'untitled'
                    
                    # Определяем формат файла из метаданных
                    output_format = metadata.get('format', 'markdown')
                    
                    # Выбираем правильное расширение файла в зависимости от формата
                    if output_format == 'rst':
                        extension = '.rst'
                    elif output_format == 'asciidoc':
                        extension = '.adoc'
                    else:  # По умолчанию markdown
                        extension = '.md'
                    
                    # Set path to new file in content directory with proper extension
                    path = f"{filename}{extension}"
                
                logger.info(f"Creating new page at: {path} with format: {metadata.get('format', 'markdown')}")
            
            # Normalize path to be relative to content directory
            if path.startswith('/'):
                path = path[1:]
                
            content_path = Path('content') / path
            
            # Проверяем если мы меняем формат существующего файла
            if not is_new_page and 'format' in metadata:
                # Получаем текущее расширение и формат из метаданных
                current_ext = Path(path).suffix
                output_format = metadata.get('format', 'markdown')
                
                # Определяем новое расширение на основе формата
                if output_format == 'rst':
                    new_ext = '.rst'
                elif output_format == 'asciidoc':
                    new_ext = '.adoc'
                else:
                    new_ext = '.md'
                
                # Если расширение изменилось, создаем новый путь
                if current_ext != new_ext:
                    # Создаем новый путь с измененным расширением
                    new_path = Path(path).with_suffix(new_ext)
                    new_content_path = Path('content') / new_path
                    
                    # Проверяем, не существует ли уже файл с таким именем
                    if new_content_path.exists():
                        return web.json_response({
                            'success': False,
                            'error': f"File already exists: {new_path}"
                        }, status=400)
                    
                    # Если старый файл существует, удаляем его после создания нового
                    should_delete_old = content_path.exists()
                    
                    # Обновляем пути
                    path = str(new_path)
                    content_path = new_content_path
                    
                    logger.info(f"Changing file format: {current_ext} -> {new_ext}, new path: {path}")
                    
                    # После сохранения нового файла, удалим старый
                    if should_delete_old:
                        logger.info(f"Will delete old file after saving new one")
            
            # Ensure parent directories exist
            content_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Преобразуем контент в выбранный формат, если нужно
            output_format = metadata.get('format', 'markdown')
            if output_format != 'markdown' and content:
                try:
                    # Импортируем необходимые парсеры
                    from ..parsers import MarkdownParser
                    
                    # Инициализируем markdown парсер для преобразования в HTML
                    md_parser = MarkdownParser()
                    
                    # Сначала получаем HTML из Markdown
                    html_content = md_parser.parse(content)
                    
                    # Преобразуем HTML в нужный формат
                    if output_format == 'rst':
                        # Импортируем HTML -> RST конвертер
                        try:
                            from html2rest import HTML2REST
                            converter = HTML2REST()
                            content = converter.convert(html_content)
                            logger.info("Converted content from Markdown to reStructuredText")
                        except ImportError:
                            logger.warning("html2rest not installed. Keeping markdown format.")
                    
                    elif output_format == 'asciidoc':
                        # Импортируем HTML -> AsciiDoc конвертер
                        try:
                            from html2asciidoc import convert
                            content = convert(html_content)
                            logger.info("Converted content from Markdown to AsciiDoc")
                        except ImportError:
                            logger.warning("html2asciidoc not installed. Keeping markdown format.")
                    
                except Exception as e:
                    logger.error(f"Error converting content format: {e}")
                    # Продолжаем с исходным контентом, если конвертация не удалась
            
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
                
            # Если мы изменили формат, удаляем старый файл
            if not is_new_page and 'format' in metadata:
                current_ext = Path(path).suffix
                old_ext = current_ext
                if output_format == 'rst':
                    old_ext = '.rst' if current_ext != '.rst' else '.md'
                elif output_format == 'asciidoc':
                    old_ext = '.adoc' if current_ext != '.adoc' else '.md'
                elif output_format == 'markdown':
                    old_ext = '.md' if current_ext != '.md' else '.rst'
                
                # Удаляем старый файл только если он существует и отличается от нового
                old_path = Path(path).with_suffix(old_ext)
                old_content_path = Path('content') / old_path
                if old_content_path.exists() and old_content_path != content_path:
                    try:
                        old_content_path.unlink()
                        logger.info(f"Deleted old file: {old_path}")
                    except Exception as e:
                        logger.error(f"Failed to delete old file: {e}")
            
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