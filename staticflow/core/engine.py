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
        self.markdown = markdown.Markdown(
            extensions=['meta', 'fenced_code'],
            extension_configs={
                'fenced_code': {
                    'lang_prefix': ''
                }
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
        
    def initialize(self, source_dir: Path, output_dir: Path, 
                  templates_dir: Path) -> None:
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

        # Use the output path already set by router in the Site.load_pages method
        if not page.output_path:
            # If for some reason output_path is not set, generate it now
            output_path = self.site.generate_page_output_path(page)
            page.set_output_path(output_path)
        else:
            output_path = page.output_path

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Use the template from config
        template_dir = self.config.get("template_dir", "templates")
        # Преобразуем к Path только если это строка
        if not isinstance(template_dir, Path):
            template_dir = Path(template_dir)
            
        template_filename = page.metadata.get(
            "template", self.config.get("default_template")
        )
        template_path = template_dir / template_filename
        
        if not template_path.exists():
            raise ValueError(f"Template not found: {template_path}")

        # Read template
        with template_path.open("r", encoding="utf-8") as f:
            template_content = f.read()

        # Convert Markdown to HTML if it's a markdown file
        if page.source_path.suffix.lower() == '.md':
            content_html = self.markdown.convert(page.content)
        else:
            content_html = page.content

        # Process content through plugins
        for plugin in self.plugins:
            content_html = plugin.process_content(content_html)

        # Get additional head content from plugins
        head_content = []
        for plugin in self.plugins:
            if hasattr(plugin, 'get_head_content'):
                head_content.append(plugin.get_head_content())

        # Simple template rendering
        html = template_content.replace("{{ page.title }}", page.title)
        html = html.replace("{{ page.content }}", content_html)
        
        # Insert head content
        if head_content:
            head_html = "\n".join(head_content)
            html = html.replace("{{ page.head_content }}", head_html)
        else:
            html = html.replace("{{ page.head_content }}", "")

        # Write the rendered page
        with output_path.open("w", encoding="utf-8") as f:
            f.write(html)
    
    def _copy_static_files(self) -> None:
        """Copy static files to the output directory."""
        if not self.site.output_dir:
            return
            
        static_dir = self.config.get("static_dir", "static")
        # Преобразуем к Path только если это строка
        if not isinstance(static_dir, Path):
            static_dir = Path(static_dir)
            
        if static_dir.exists():
            output_static = self.site.output_dir / "static"
            if output_static.exists():
                shutil.rmtree(output_static)
            shutil.copytree(static_dir, output_static)
            
    def clean(self) -> None:
        """Clean the build artifacts."""
        if self.site.output_dir and self.site.output_dir.exists():
            shutil.rmtree(self.site.output_dir)
        self._cache.clear()
        self.site.clear()
        
        # Cleanup plugins
        for plugin in self.plugins:
            plugin.cleanup()