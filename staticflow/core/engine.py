from pathlib import Path
import shutil
import markdown
from typing import List, Optional, Dict, Any
from .config import Config
from .site import Site
from .page import Page
from ..plugins.base import Plugin


class Engine:
    """Main engine for static site generation."""
    
    def __init__(self, config):
        """Initialize engine with config."""
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, (str, Path)):
            self.config = Config(config)
        else:
            raise TypeError(
                "config must be Config instance or path-like object"
            )
        self.site = Site(self.config)
        self._cache = {}
        
        # Настраиваем Markdown с особым вниманием к подсветке кода
        fenced_code_config = {
            'lang_prefix': 'language-',  # Важно! Добавляет префикс language- к классу
        }
        
        self.markdown = markdown.Markdown(
            extensions=[
                'meta',
                'fenced_code',
                'tables',
                'attr_list',
            ],
            extension_configs={
                'fenced_code': fenced_code_config
            }
        )
        self.plugins: List[Plugin] = []
        
    def add_plugin(self, plugin: Plugin, config: Optional[Dict[str, Any]] = None) -> None:
        """Add a plugin to the engine with optional configuration."""
        plugin.engine = self
        if config:
            plugin.config = config
        plugin.initialize()
        self.plugins.append(plugin)
        
    def initialize(self, source_dir: Path, output_dir: Path, templates_dir: Path) -> None:
        """Initialize the engine with directory paths."""
        self.site.set_directories(source_dir, output_dir, templates_dir)
        
    def build(self) -> None:
        """Build the site."""
        # Create output directory if it doesn't exist
        if self.site.output_dir:
            self.site.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Execute pre-build hooks
        for plugin in self.plugins:
            if hasattr(plugin, 'pre_build'):
                plugin.pre_build(self.site)
            
        self.site.clear()
        
        # Load pages before processing them
        self.site.load_pages()
        
        self._process_pages()
        
        # Execute post-build hooks
        for plugin in self.plugins:
            if hasattr(plugin, 'post_build'):
                plugin.post_build(self.site)
            
        # Копируем статику админки в папку public
        try:
            from ..admin import AdminPanel
            admin = AdminPanel(self.config, self)
            admin.copy_static_to_public()
        except Exception as e:
            print(f"Ошибка при копировании статики админки: {e}")
            
        # Copy static files
        self._copy_static_files()
        
    def _process_pages(self) -> None:
        """Process all pages in the site."""
        for page in self.site.get_all_pages():
            self._process_page(page)
            
    def _process_page(self, page: Page) -> None:
        """Process a single page."""
        if not self.site.source_dir or not self.site.output_dir:
            raise ValueError("Source and output directories must be set")

        if not page.output_path:
            output_path = self.site.generate_page_output_path(page)
            page.set_output_path(output_path)
        else:
            output_path = page.output_path

        output_path.parent.mkdir(parents=True, exist_ok=True)

        template_dir = self.config.get("template_dir", "templates")
        if not isinstance(template_dir, Path):
            template_dir = Path(template_dir)
        template_filename = page.metadata.get("template", self.config.get("default_template"))

        static_url = self.config.get("static_url", "static")

        if static_url.startswith('/') or static_url.startswith('http'):
            # Уже абсолютный путь, оставляем как есть
            pass
        else:
            # Добавляем / в начало для локальной разработки
            static_url = f"/{static_url}"

        # Убираем лишний слеш в конце, если он есть
        static_url = static_url.rstrip('/')

        # Конвертация контента в HTML
        if page.source_path.suffix.lower() == '.md':
            content_html = self.markdown.convert(page.content)
        elif page.source_path.suffix.lower() == '.rst':
            from ..parsers import RSTParser
            rst_parser = RSTParser()
            content_html = rst_parser.parse(page.content)
        else:
            content_html = page.content

        for plugin in self.plugins:
            content_html = plugin.process_content(content_html)
        head_content = []
        for plugin in self.plugins:
            if hasattr(plugin, 'get_head_content'):
                head_content.append(plugin.get_head_content())

        translations = self.site.get_page_translations(page)
        translation_urls = self.site.get_page_translation_urls(page)

        available_translations = translation_urls.copy()
        if page.output_path:
            try:
                # Добавляем текущий язык и URL
                current_url = "/" + str(page.output_path.relative_to(self.site.output_dir))
                available_translations[page.language] = current_url
            except (ValueError, TypeError):
                pass

        context = {
            "page": page,
            "site_name": self.config.get("site_name", "StaticFlow Site"),
            "site_url": self.config.get("base_url", ""),
            "static_url": static_url,
            "page_content": content_html,
            "page_head_content": "\n".join(head_content) if head_content else "",
            "translations": translations,
            "available_translations": available_translations,
        }

        page.translations = translation_urls

        from staticflow.templates.engine import TemplateEngine
        engine = TemplateEngine(template_dir)
        html = engine.render(template_filename, context)
        with output_path.open("w", encoding="utf-8") as f:
            f.write(html)

    def _copy_static_files(self) -> None:
        """Copy static files to the output directory."""
        if not self.site.output_dir:
            return

        static_dir = self.config.get("static_dir", "static")
        if not isinstance(static_dir, Path):
            static_dir = Path(static_dir)
            
        if static_dir.exists():
            output_static = self.site.output_dir / "static"
            if output_static.exists():
                shutil.rmtree(output_static)
            shutil.copytree(static_dir, output_static)
            
        # Генерируем code_highlight.css на основе стиля из конфига
        self._generate_code_highlight_css(static_dir)
            
    def _generate_code_highlight_css(self, static_dir: Path) -> None:
        """Generate code highlight CSS based on configuration."""
        try:
            # Создаем директорию css, если её нет
            css_dir = static_dir / "css"
            css_dir.mkdir(parents=True, exist_ok=True)
            
            # Получаем стиль подсветки из конфига
            syntax_config = self.config.get("syntax_highlight", {})
            style_name = syntax_config.get("style", "monokai")
            
            # Генерируем CSS
            from ..utils.pygments_utils import generate_pygments_css
            css_content = generate_pygments_css(style_name)
            
            # Записываем в файл
            css_file = css_dir / "code_highlight.css"
            with open(css_file, "w", encoding="utf-8") as f:
                f.write(css_content)
                
            print(f"Generated code highlight CSS with '{style_name}' style")
            
        except Exception as e:
            print(f"Error generating code highlight CSS: {e}")
            
    def clean(self) -> None:
        """Clean the build artifacts."""
        if self.site.output_dir and self.site.output_dir.exists():
            shutil.rmtree(self.site.output_dir)
        self._cache.clear()
        self.site.clear()
        
        # Cleanup plugins
        for plugin in self.plugins:
            plugin.cleanup()

    def load_page_from_file(self, file_path: Path) -> Optional[Page]:
        """
        Load a page from a file.
        This method is used by the admin panel to get page data for URL generation.
        """
        try:
            default_language = self.config.get_default_language()
            page = Page.from_file(file_path, default_lang=default_language)

            if self.site.source_dir:
                try:
                    page.source_path = file_path.relative_to(self.site.source_dir)
                except ValueError:
                    page.source_path = file_path

            return page
        except Exception as e:
            print(f"Error loading page from file {file_path}: {e}")
            return None

    def render_page(self, page: Page) -> str:
        """Render a Page object to HTML (for preview, no disk write)."""
        template_dir = self.config.get("template_dir", "templates")
        if not isinstance(template_dir, Path):
            template_dir = Path(template_dir)
        template_filename = page.metadata.get("template", self.config.get("default_template", "page.html"))
        template_path = template_dir / template_filename
        if not template_path.exists():
            raise ValueError(f"Template not found: {template_path}")

        # Markdown → HTML
        content_html = self.markdown.convert(page.content)
        for plugin in self.plugins:
            content_html = plugin.process_content(content_html)

        head_content = []
        for plugin in self.plugins:
            if hasattr(plugin, 'get_head_content'):
                head_content.append(plugin.get_head_content())

        # Получаем static_url с учетом правильного пути
        static_url = self.config.get("static_url", "static")
        
        # При локальной разработке делаем абсолютный путь с / в начале
        # Для GitHub Pages static_url должен уже содержать корректный путь с repo_name
        if static_url.startswith('/') or static_url.startswith('http'):
            # Уже абсолютный путь, оставляем как есть
            pass
        else:
            # Добавляем / в начало для локальной разработки
            static_url = f"/{static_url}"
        
        # Убираем лишний слеш в конце, если он есть
        static_url = static_url.rstrip('/')
            
        context = {
            "page": page,
            "site_name": self.config.get("site_name", "StaticFlow Site"),
            "site_url": self.config.get("base_url", ""),  
            "static_url": static_url,
            "page_content": content_html,
            "page_head_content": "\n".join(head_content) if head_content else "",
            "available_translations": {},  # Пустой словарь для предпросмотра
        }
        page.translations = {}

        from staticflow.templates.engine import TemplateEngine
        engine = TemplateEngine(template_dir)
        return engine.render(template_filename, context)