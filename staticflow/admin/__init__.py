from pathlib import Path
from aiohttp import web
import aiohttp_jinja2
import jinja2
from ..core.config import Config
from ..core.engine import Engine
import json


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
        
        # Добавляем маршруты для блочного редактора
        self.app.router.add_get('/block-editor', self.block_editor_handler)
        self.app.router.add_get('/block-editor/{path:.*}', self.block_editor_handler)
        self.app.router.add_post('/api/preview', self.api_preview_handler)
        
        # Добавляем статические файлы
        static_path = Path(__file__).parent / 'static'
        print(f"Static path: {static_path} (exists: {static_path.exists()})")
        
        if not static_path.exists():
            static_path.mkdir(parents=True)
            print(f"Created static directory: {static_path}")
            
        self.app.router.add_static('/static', static_path)
        
    async def handle_request(self, request):
        """Handle admin panel request."""
        print(f"Admin request: {request.path}, method: {request.method}")
        
        # Remove /admin prefix from path
        path = request.path.replace('/admin', '', 1)
        if not path:
            path = '/'
            
        print(f"Modified path: {path}")
        
        # Прямое перенаправление для API запросов без клонирования
        if request.method == 'POST' and path.startswith('/api/'):
            # Маршрутизация API напрямую к обработчикам
            if path == '/api/content':
                return await self.api_content_handler(request)
            elif path == '/api/preview':
                return await self.api_preview_handler(request)
            elif path == '/api/settings':
                return await self.api_settings_handler(request)
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
            print(f"Admin page not found: {path}")
            return web.Response(status=404, text="Admin page not found")
        except Exception as e:
            print(f"Error handling admin request: {e}")
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
        
    @aiohttp_jinja2.template('block_editor.html')
    async def block_editor_handler(self, request):
        """Handle block editor page."""
        path = request.match_info.get('path', '')
        page = None
        safe_metadata = {}
        
        if path:
            content_path = Path('content') / path
            print(f"Attempting to load page from: {content_path}")
            if content_path.exists():
                try:
                    # Создаем объект Page из существующего файла
                    from ..core.page import Page
                    page = Page.from_file(content_path)
                    
                    # Устанавливаем правильный путь к исходному файлу
                    page.source_path = path
                    
                    # Преобразуем метаданные в JSON-безопасный формат
                    safe_metadata = self._safe_metadata(page.metadata)
                    
                    print(f"Successfully loaded page: {path}")
                    print(f"Page content length: {len(page.content)}")
                    print(f"Page metadata: {page.metadata}")
                    print(f"Safe metadata: {safe_metadata}")
                except Exception as e:
                    print(f"Error loading page: {e}")
                    import traceback
                    traceback.print_exc()
        
        return {
            'page': page,
            'safe_metadata': safe_metadata
        }
        
    async def api_content_handler(self, request):
        """Handle content API requests."""
        print("api_content_handler called")
        
        # Проверка метода
        if request.method != 'POST':
            print(f"Method not allowed: {request.method}")
            return web.json_response({
                'success': False,
                'error': f"Method not allowed: {request.method}"
            }, status=405)
        
        # Печатаем все заголовки для отладки
        print("Request headers:")
        for header_name, header_value in request.headers.items():
            print(f"  {header_name}: {header_value}")
        
        # Проверка наличия тела запроса 
        content_length = request.content_length
        print(f"Content-Length: {content_length}")
        
        content_type = request.headers.get('Content-Type', '')
        print(f"Content-Type: {content_type}")
        
        if content_type != 'application/json':
            print(f"Invalid Content-Type: {content_type}")
            return web.json_response({
                'success': False,
                'error': f"Invalid Content-Type: {content_type}, expected application/json"
            }, status=400)
            
        try:
            # Проверка читабельности тела запроса без вызова async методов
            if not request.can_read_body:
                print("Request has no body (can_read_body is False)")
                return web.json_response({
                    'success': False,
                    'error': "Request has no body (can_read_body is False)"
                }, status=400)
            
            if request.content_length is None or request.content_length <= 0:
                print("Request has empty content length")
                return web.json_response({
                    'success': False,
                    'error': "Request has empty content length"
                }, status=400)
            
            try:
                # Прямое чтение тела запроса как строки для отладки
                raw_body = await request.text()
                print(f"Raw request body ({len(raw_body)} bytes): {raw_body[:200]}...")
                
                if not raw_body:
                    print("Request body is empty")
                    return web.json_response({
                        'success': False, 
                        'error': "Request body is empty"
                    }, status=400)
                
                # Явный разбор JSON
                try:
                    data = json.loads(raw_body)
                except json.JSONDecodeError as e:
                    print(f"JSON parse error: {e}, body: {raw_body}")
                    return web.json_response({
                        'success': False, 
                        'error': f"Invalid JSON: {e}"
                    }, status=400)
            
                print(f"Request data keys: {list(data.keys())}")
                
                # Проверка необходимых полей
                if 'path' in data and 'content' in data:
                    # Сохранение контента из блочного редактора
                    path_str = data['path']
                    content = data['content']
                    metadata = data.get('metadata', {})
                    
                    print(f"Received request to save content to {path_str}")
                    print(f"Content length: {len(content)}")
                    print(f"Metadata: {metadata}")
                    
                    # Если это новая страница, генерируем имя файла из заголовка
                    if path_str == 'New Page' and 'title' in metadata:
                        import re
                        from datetime import datetime
                        
                        # Создаем slug из заголовка
                        slug = re.sub(r'[^\w\s-]', '', metadata['title'].lower())
                        slug = re.sub(r'[\s-]+', '-', slug).strip('-_')
                        
                        # Добавляем дату к имени файла
                        date_prefix = datetime.now().strftime('%Y-%m-%d')
                        path_str = f"{date_prefix}-{slug}.md"
                    
                    # Создаем полный путь к файлу
                    path = Path('content')
                    path.mkdir(exist_ok=True)
                    
                    full_path = path / path_str
                    
                    # Создаем контент с правильными метаданными
                    final_content = '---\n'
                    for key, value in metadata.items():
                        if isinstance(value, list):
                            value_str = '[' + ', '.join(f'"{item}"' for item in value) + ']'
                            final_content += f"{key}: {value_str}\n"
                        else:
                            final_content += f"{key}: {value}\n"
                    final_content += '---\n\n'
                    
                    # Добавляем основной контент без frontmatter, если он есть
                    content_without_frontmatter = content
                    if content.startswith('---'):
                        parts = content.split('---', 2)
                        if len(parts) >= 3:
                            content_without_frontmatter = parts[2].strip()
                    
                    final_content += content_without_frontmatter
                    
                    # Записываем в файл
                    try:
                        full_path.write_text(final_content, encoding='utf-8')
                        print(f"Content successfully saved to {full_path}")
                        
                        # Пересобираем сайт после изменения контента
                        print("Starting site rebuild after content change...")
                        rebuild_success = self.rebuild_site()
                        
                        if rebuild_success:
                            return web.json_response({
                                'success': True,
                                'path': path_str,
                                'message': "Content saved and site rebuilt successfully"
                            })
                        else:
                            return web.json_response({
                                'success': True,
                                'path': path_str,
                                'warning': "Content saved but site rebuild failed"
                            })
                    except Exception as e:
                        print(f"Error saving content: {e}")
                        import traceback
                        traceback.print_exc()
                        return web.json_response({
                            'success': False,
                            'error': str(e)
                        }, status=500)
                
                # Обработка стандартного API (для обратной совместимости)
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
                    self.rebuild_site()
                    return web.json_response({'status': 'ok'})
                    
                elif action == 'update':
                    # Update existing content file
                    path = Path('content') / data['path']
                    path.write_text(data['content'], encoding='utf-8')
                    self.rebuild_site()
                    return web.json_response({'status': 'ok'})
                    
                elif action == 'delete':
                    # Delete content file
                    path = Path('content') / data['path']
                    path.unlink(missing_ok=True)
                    self.rebuild_site()
                    return web.json_response({'status': 'ok'})
            
            except Exception as e:
                print(f"Error processing request body: {e}")
                import traceback
                traceback.print_exc()
                return web.json_response({
                    'success': False,
                    'error': str(e)
                }, status=500)
        
        except Exception as e:
            print(f"Unexpected error in api_content_handler: {e}")
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
            
            # Рендерим контент напрямую, без создания Page
            try:
                # Рендерим контент напрямую с помощью стандартной библиотеки markdown
                import markdown
                # Добавляем базовые расширения, которые точно работают
                html_content = markdown.markdown(content, extensions=['fenced_code', 'tables', 'nl2br'])
                
                # Оборачиваем HTML в базовый шаблон для предпросмотра с улучшенными стилями
                preview_html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{metadata.get('title', 'Preview')}</title>
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
                        }}
                    </style>
                    <!-- Подключаем внешние библиотеки для специальных элементов -->
                    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
                    <script>
                        document.addEventListener('DOMContentLoaded', function() {{
                            // Инициализация Mermaid для диаграмм
                            mermaid.initialize({{startOnLoad:true}});
                            
                            // Преобразуем блоки с диаграммами
                            const preElements = document.querySelectorAll('pre code.mermaid');
                            preElements.forEach(function(codeBlock) {{
                                const parent = codeBlock.parentNode;
                                const content = codeBlock.textContent;
                                const div = document.createElement('div');
                                div.className = 'mermaid';
                                div.textContent = content;
                                parent.parentNode.replaceChild(div, parent);
                            }});
                        }});
                    </script>
                </head>
                <body>
                    <h1>{metadata.get('title', 'Preview')}</h1>
                    {html_content}
                </body>
                </html>
                """
                
                return web.Response(
                    text=preview_html,
                    content_type='text/html'
                )
            except Exception as e:
                print(f"Error generating preview: {e}")
                return web.json_response({
                    'success': False,
                    'error': f"Error generating preview: {e}"
                }, status=500)
        except json.JSONDecodeError as e:
            print(f"Preview JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            print(f"Unexpected error in api_preview_handler: {e}")
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
            print(f"Settings JSON parse error: {e}")
            return web.json_response({
                'success': False,
                'error': f"Invalid JSON: {e}"
            }, status=400)
        except Exception as e:
            print(f"Unexpected error in api_settings_handler: {e}")
            import traceback
            traceback.print_exc()
            return web.json_response({
                'success': False,
                'error': str(e)
            }, status=500)
        
    def rebuild_site(self):
        """Rebuild the site."""
        print("Rebuilding site...")
        try:
            # Очищаем кеш перед перестроением
            print("Clearing cache...")
            self.engine._cache.clear()
            if hasattr(self.engine.site, 'clear'):
                print("Clearing site data...")
                self.engine.site.clear()
            
            # Перезагружаем конфигурацию
            print("Reloading configuration...")
            if hasattr(self.engine.config, 'reload'):
                self.engine.config.reload()
            
            # Пересобираем сайт с нуля
            print("Building site from scratch...")
            
            # Перед перестроением проверим все директории
            source_dir = Path(self.engine.config.get("source_dir", "content"))
            output_dir = Path(self.engine.config.get("output_dir", "public"))
            templates_dir = Path(self.engine.config.get("template_dir", "templates"))
            
            print(f"Source directory: {source_dir} (exists: {source_dir.exists()})")
            print(f"Output directory: {output_dir} (exists: {output_dir.exists()})")
            print(f"Templates directory: {templates_dir} (exists: {templates_dir.exists()})")
            
            # Очистим выходную директорию, если она существует
            if output_dir.exists():
                import shutil
                print(f"Removing old output directory: {output_dir}")
                shutil.rmtree(output_dir)
                output_dir.mkdir(parents=True)
                print("Output directory recreated")

            # Полностью переинициализируем сайт
            self.engine.initialize(source_dir, output_dir, templates_dir)

            # Перестраиваем сайт
            self.engine.build()
            
            content_count = len(list(source_dir.rglob("*.md")))
            pages_generated = len(list(output_dir.rglob("*.html")))
            
            print(f"Site rebuilt successfully! Content files: {content_count}, Pages generated: {pages_generated}")
            
            return True
        except Exception as e:
            print(f"Error rebuilding site: {e}")
            import traceback
            traceback.print_exc()
            return False
            
    def start(self, host: str = 'localhost', port: int = 8001):
        """Start the admin panel server."""
        web.run_app(self.app, host=host, port=port) 