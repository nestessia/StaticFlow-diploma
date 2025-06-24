from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..core.config import Config
from ..core.engine import Engine
import json
import re
import shutil
from ..utils.logging import get_logger
import uuid

logger = get_logger("admin")


class AdminPanel:
    """Admin panel for StaticFlow."""

    def __init__(self, config: Config, engine: Engine):
        self.config = config
        self.engine = engine
        self.output_dir = Path(self.config.get('output_dir'))
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
                result[key] = value.isoformat()
            elif isinstance(value, (str, int, float, bool, type(None))):
                result[key] = value
            elif isinstance(value, list):
                safe_list = []
                for item in value:
                    if isinstance(item, (str, int, float, bool)):
                        safe_list.append(item)
                    else:
                        safe_list.append(str(item))
                result[key] = safe_list
            else:
                result[key] = str(value)

        return result

    def setup_templates(self):
        """Setup Jinja2 templates for admin panel and site preview (project-aware)."""
        from pathlib import Path
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
        self.app.router.add_get('/', self.index_handler)
        self.app.router.add_get('/content', self.index_handler)
        self.app.router.add_post('/api/content', self.api_content_handler)
        self.app.router.add_get('/block-editor', self.block_editor_handler)
        self.app.router.add_get('/block-editor/{path:.*}', self.block_editor_handler)
        self.app.router.add_get('/deploy', self.deploy_handler)
        self.app.router.add_get('/api/deploy/config', self.api_deploy_config_get_handler)
        self.app.router.add_post('/api/deploy/config', self.api_deploy_config_handler)
        self.app.router.add_post('/api/deploy/start', self.api_deploy_start_handler)
        self.app.router.add_post('/api/upload', self.api_upload_handler)
        
        # Статические файлы админки
        static_path = Path(__file__).parent / 'static'
        if not static_path.exists():
            static_path.mkdir(parents=True)
        cached_static_path = Path('output/admin/static')
        use_cached = cached_static_path.exists()
        final_static_path = cached_static_path if use_cached else static_path
        self.app.router.add_static('/static', final_static_path)
        
        # Статические медиафайлы теперь из output_dir/media
        media_path = self.output_dir / 'media'
        if not media_path.exists():
            media_path.mkdir(parents=True)
        self.app.router.add_static('/media', media_path)
        
        if not use_cached:
            self.copy_static_to_output()

    async def handle_request(self, request):
        """Handle admin panel request."""
        logger.info(f"Admin request: {request.path}, method: {request.method}")

        path = request.path.replace('/admin', '', 1)
        if not path:
            path = '/'

        logger.info(f"Modified path: {path}")

        if path.startswith('/api/'):
            if request.method == 'GET':
                if path == '/api/deploy/config':
                    return await self.api_deploy_config_get_handler(request)

            if request.method == 'POST':
                if path == '/api/content':
                    return await self.api_content_handler(request)
                elif path == '/api/deploy/config':
                    return await self.api_deploy_config_handler(request)
                elif path == '/api/deploy/start':
                    return await self.api_deploy_start_handler(request)
                elif path == '/api/upload':
                    return await self.api_upload_handler(request)
                else:
                    return web.json_response({
                        'success': False,
                        'error': f"Unknown API endpoint: {path}"
                    }, status=404)

        try:
            subrequest = request.clone(rel_url=path)
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
        content_path = Path('content')
        files = []

        engine = self.engine
        site = engine.site
        base_url = self.config.get('base_url', '')

        for file in content_path.rglob('*.*'):
            if file.suffix in ['.md', '.html']:
                rel_path = str(file.relative_to(content_path)).replace('\\', '/')
                print(f"DEBUG: rel_path={rel_path!r} for file={file}")
                if not rel_path:
                    continue

                file_url = ""
                try:
                    page = engine.load_page_from_file(file)
                    if page:
                        content_type = site.determine_content_type(page)

                        file_url = site.router.get_url(content_type, page.metadata)

                        if file_url and not file_url.startswith('http'):
                            if not file_url.startswith('/'):
                                file_url = '/' + file_url
                            file_url = f"{base_url.rstrip('/')}{file_url}"
                except Exception as e:
                    logger.error(f"Error generating URL for {rel_path}: {e}")

                if not file_url:
                    file_url = f"{base_url.rstrip('/')}/" + re.sub(r'\.md$', '.html', rel_path)

                files.append({
                    'path': rel_path,
                    'modified': file.stat().st_mtime,
                    'size': file.stat().st_size,
                    'url': file_url
                })

        static_dir = self.config.get("static_dir", "static")
        static_dir = "/" + str(static_dir).strip("/")
        return {
            'files': files,
            'static_dir': static_dir,
        }

    @aiohttp_jinja2.template('deploy.html')
    async def deploy_handler(self, request):
        """Handle deployment page."""
        from ..deploy.github_pages import GitHubPagesDeployer
        deployer = GitHubPagesDeployer()

        status = deployer.get_deployment_status()

        static_dir = self.config.get("static_dir", "static")
        static_dir = "/" + str(static_dir).strip("/")
        return {
            'status': status,
            'config': status['config'],
            'static_dir': static_dir,
        }

    @aiohttp_jinja2.template('block_editor.html')
    async def block_editor_handler(self, request):
        """Handle block editor page."""
        path = request.match_info.get('path', '')
        page = None
        safe_metadata = {}
        error_message = None
        import logging
        logger = logging.getLogger("admin.block_editor_handler")
        if path:
            content_path = Path('content') / path
            logger.info(f"Attempting to load page from: {content_path}")
            if content_path.exists():
                try:
                    from ..core.page import Page
                    page = Page.from_file(content_path)
                    page.source_path = path
                    if not hasattr(page, 'modified'):
                        page.modified = content_path.stat().st_mtime
                    safe_metadata = self._safe_metadata(page.metadata)
                    logger.info(f"Successfully loaded page: {path}")
                except Exception as e:
                    logger.error(f"Error loading page: {e}")
                    import traceback
                    traceback.print_exc()
                    error_message = f"Ошибка загрузки файла: {e}"
            else:
                logger.error(f"File does not exist: {content_path}")
                error_message = f"Файл не найден: {content_path}"
        return {
            'page': page,
            'safe_metadata': safe_metadata,
            'error_message': error_message
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

            is_new_page = path == 'New Page'
            if is_new_page:
                if '.' in path and path != 'New Page':
                    logger.info(f"Using provided path for new page: {path}")
                else:
                    title = metadata.get('title', 'Untitled')
                    filename = title.lower().replace(' ', '-')
                    filename = re.sub(r'[^a-z0-9\-_]', '', filename)
                    if not filename:
                        filename = 'untitled'

                    output_format = metadata.get('format', 'markdown')

                    if output_format == 'html':
                        extension = '.html'
                    else:
                        extension = '.md'

                    path = f"{filename}{extension}"

                logger.info(f"Creating new page at: {path} with format: {metadata.get('format', 'markdown')}")

            if path.startswith('/'):
                path = path[1:]

            content_path = Path('content') / path

            if not is_new_page and 'format' in metadata:
                current_ext = Path(path).suffix
                output_format = metadata.get('format', 'markdown')

            content_path.parent.mkdir(parents=True, exist_ok=True)

            frontmatter = '---\n'
            for key, value in metadata.items():
                if isinstance(value, list):
                    frontmatter += f"{key}:\n"
                    for item in value:
                        frontmatter += f"  - {item}\n"
                else:
                    frontmatter += f"{key}: {value}\n"
            frontmatter += '---\n\n'

            with open(content_path, 'w', encoding='utf-8') as f:
                f.write(frontmatter + content)

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


    async def api_deploy_config_get_handler(self, request):
        """Handle deploy configuration GET API requests."""
        try:
            from ..deploy.github_pages import GitHubPagesDeployer
            deployer = GitHubPagesDeployer()

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

            from ..deploy.github_pages import GitHubPagesDeployer
            deployer = GitHubPagesDeployer()

            deployer.update_config(**data)

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
            data = {}
            try:
                data = await request.json()
                logger.info(f"Received deployment data: {data}")
            except json.JSONDecodeError:
                logger.info("No JSON data provided in request")
                pass

            commit_message = data.get('commit_message')
            logger.info(f"Using commit message: {commit_message or 'default'}")

            from ..deploy.github_pages import GitHubPagesDeployer
            logger.info("Initializing GitHubPagesDeployer")
            deployer = GitHubPagesDeployer()

            repo_url = deployer.config.get("repo_url", "")

            logger.info("Validating deployment configuration")
            is_valid, errors, warnings = deployer.validate_config()
            if not is_valid:
                logger.error(f"Invalid configuration: {errors}")
                return web.json_response({
                    'success': False,
                    'message': f"Invalid configuration: {', '.join(errors)}"
                }, status=400)

            original_base_url = self.config.get("base_url")
            original_static_dir = self.config.get("static_dir")
            
            try:
                self._update_config_for_github_pages(repo_url)

                logger.info("Rebuilding site before deployment")
                rebuild_success = self.rebuild_site()
                if not rebuild_success:
                    logger.error("Failed to build site")
                    return web.json_response({
                        'success': False,
                        'message': 'Failed to build site'
                    }, status=500)

                logger.info("Site successfully rebuilt, starting deployment")

                logger.info(f"Deploying site with committer: {deployer.config.get('username')}")
                success, message = deployer.deploy(commit_message=commit_message)
                logger.info(f"Deployment result: success={success}, message={message}")

                status = deployer.get_deployment_status()

                logger.info("=== Deployment process completed ===")
                return web.json_response({
                    'success': success,
                    'message': message,
                    'timestamp': status.get('last_deployment'),
                    'history': status.get('history', []),
                    'warnings': warnings
                })
            finally:
                logger.info("Восстанавливаем оригинальные настройки конфигурации")
                self.config.set("base_url", original_base_url)
                self.config.set("static_dir", original_static_dir)
                rebuild_success = self.rebuild_site()
                if not rebuild_success:
                    logger.warning("Не удалось пересобрать сайт после восстановления настроек")
                logger.info(f"Конфигурация восстановлена: base_url={original_base_url}, static_dir={original_static_dir}")
        except Exception as e:
            logger.error(f"Critical error in api_deploy_start_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'message': f"Deployment failed: {str(e)}"
            }, status=500)

    def _update_config_for_github_pages(self, repo_url):
        """Обновляет конфигурацию для GitHub Pages"""

        repo_name = self._extract_repo_name(repo_url)
        if not repo_name:
            logger.warning("Не удалось извлечь имя репозитория из URL, оставляем конфигурацию без изменений")
            return
        
        logger.info(f"Обновляем конфигурацию для GitHub Pages репозитория: {repo_name}")

        username = None
        if repo_url.startswith("https://github.com/"):
            parts = repo_url.split("https://github.com/")[1].split("/")
            if len(parts) >= 1:
                username = parts[0]
        elif repo_url.startswith("git@github.com:"):
            parts = repo_url.split("git@github.com:")[1].split("/")
            if len(parts) >= 1:
                username = parts[0]

        if not username:
            logger.warning("Не удалось извлечь имя пользователя из URL, оставляем конфигурацию без изменений")
            return

        base_url = f"https://{username}.github.io/{repo_name}"
        logger.info(f"Устанавливаем base_url: {base_url}")

        self.config.set("base_url", base_url)
        self.config.set("static_dir", f"{repo_name}/static/")

        logger.info(f"Конфигурация обновлена: base_url={base_url}, static_dir={repo_name}/static/")

    def _extract_repo_name(self, repo_url):
        """Извлекает имя репозитория из URL GitHub"""
        if not repo_url:
            return None

        if repo_url.startswith("https://github.com/"):
            parts = repo_url.split("https://github.com/")[1].split("/")
            if len(parts) >= 2:
                return parts[1].replace(".git", "")

        elif repo_url.startswith("git@github.com:"):
            parts = repo_url.split("git@github.com:")[1].split("/")
            if len(parts) >= 2:
                return parts[1].replace(".git", "")

        return None

    def copy_static_to_output(self):
        """Копирует статические файлы админки в папку output_dir для кэширования."""
        source_static_path = Path(__file__).parent / 'static'
        if not source_static_path.exists():
            logger.info("Исходная директория статики не существует, нечего копировать")
            return

        dest_static_path = self.output_dir / 'admin' / 'static'

        dest_static_path.parent.mkdir(parents=True, exist_ok=True)

        if dest_static_path.exists():
            shutil.rmtree(dest_static_path)
        shutil.copytree(source_static_path, dest_static_path)

    def rebuild_site(self):
        """Rebuild the site using the engine."""
        try:
            self.copy_static_to_output()

            self.engine.build()
            return True
        except Exception as e:
            logger.error(f"Error rebuilding site: {e}")
            import traceback
            traceback.print_exc()
            return False

    async def api_upload_handler(self, request):
        """Handle file upload requests."""
        try:
            reader = await request.multipart()
            field = await reader.next()
            
            if not field or field.name != 'file':
                return web.json_response({
                    'success': False,
                    'error': 'No file field in request'
                }, status=400)

            filename = field.filename
            if not filename:
                return web.json_response({
                    'success': False,
                    'error': 'No filename provided'
                }, status=400)

            # Создаем директорию media в output_dir если её нет
            media_dir = self.output_dir / 'media'
            media_dir.mkdir(parents=True, exist_ok=True)

            # Генерируем уникальное имя файла
            ext = Path(filename).suffix
            unique_filename = f"{uuid.uuid4().hex}{ext}"
            file_path = media_dir / unique_filename

            # Сохраняем файл
            with open(file_path, 'wb') as f:
                while True:
                    chunk = await field.read_chunk()
                    if not chunk:
                        break
                    f.write(chunk)

            # Возвращаем URL для доступа к файлу
            url = f"/media/{unique_filename}"
            
            return web.json_response({
                'success': True,
                'url': url
            })

        except Exception as e:
            logger.error(f"Error in api_upload_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)

    def start(self, host: str = 'localhost', port: int = 8001):
        """Start the admin panel server."""
        web.run_app(self.app, host=host, port=port)

__all__ = ['AdminPanel']