from pathlib import Path
import shutil
import markdown
from typing import List, Optional, Dict, Any
from .config import Config
from .site import Site
from .page import Page
from ..plugins.base import Plugin
from ..parsers.extensions.video import makeExtension as makeVideoExtension
from ..parsers.extensions.audio import makeExtension as makeAudioExtension
from ..utils.logging import get_logger


logger = get_logger("core.engine")


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

        fenced_code_config = {
            'lang_prefix': 'language-',
        }

        self.markdown = markdown.Markdown(
            extensions=[
                'meta',
                'fenced_code',
                'tables',
                'attr_list',
                makeVideoExtension(),
                makeAudioExtension(),
            ],
            extension_configs={
                'fenced_code': fenced_code_config
            }
        )
        self.plugins: List[Plugin] = []
        logger.info("Engine initialized")

    def add_plugin(self, plugin: Plugin,
                   config: Optional[Dict[str, Any]] = None) -> None:
        """Add a plugin to the engine with optional configuration."""
        plugin.engine = self
        if config:
            plugin.config = config
        plugin.initialize()
        self.plugins.append(plugin)
        logger.info(
            "Plugin added: %s",
            plugin.metadata.name if hasattr(plugin, 'metadata')
            else plugin.__class__.__name__
        )

    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Get a plugin by its name."""
        for plugin in self.plugins:
            if hasattr(plugin, 'metadata') and plugin.metadata.name == name:
                return plugin
        return None

    def initialize(self, source_dir: Path, output_dir: Path, templates_dir: Path) -> None:
        """Initialize the engine with directory paths."""
        if isinstance(source_dir, str):
            source_dir = Path(source_dir)
        if isinstance(output_dir, str):
            output_dir = Path(output_dir)
        if isinstance(templates_dir, str):
            templates_dir = Path(templates_dir)
        self.site.set_directories(
            source_dir,
            output_dir,
            templates_dir
        )
        logger.info(
            "Engine directories initialized: source=%s, output=%s, templates=%s",
            source_dir,
            output_dir,
            templates_dir
        )

    def build(self) -> None:
        """Build the site."""
        logger.info("Starting site build")

        if self.site.output_dir:
            self.site.output_dir.mkdir(parents=True, exist_ok=True)
            logger.debug("Output directory created/verified: %s", self.site.output_dir)

        for plugin in self.plugins:
            if hasattr(plugin, 'pre_build'):
                logger.debug("Running pre_build hook for plugin: %s", plugin.metadata.name if hasattr(plugin, 'metadata') else plugin.__class__.__name__)
                plugin.pre_build(self.site)

        logger.info("Clearing site and loading pages")
        self.site.clear()
        self.site.load_pages()
        logger.info("Processing pages")
        self._process_pages()

        for plugin in self.plugins:
            if hasattr(plugin, 'post_build'):
                logger.debug("Running post_build hook for plugin: %s", plugin.metadata.name if hasattr(plugin, 'metadata') else plugin.__class__.__name__)
                plugin.post_build(self.site)

        try:
            from ..admin import AdminPanel
            logger.debug("Copying admin static files")
            admin = AdminPanel(self.config, self)
            admin.copy_static_to_output()
        except Exception as e:
            logger.error("Error copying admin static files: %s", e)

        logger.debug("Copying static files")
        self._copy_static_files()
        logger.info("Site build completed")

    def _process_pages(self) -> None:
        """Process all pages in the site."""
        pages = self.site.get_all_pages()
        logger.info("Processing %d pages", len(pages))
        for page in pages:
            logger.debug("Processing page: %s", page.url)
            self._process_page(page)

    def _process_page(self, page: Page) -> None:
        """Process a single page."""
        try:
            content = self.markdown.convert(page.content)

            for plugin in self.plugins:
                if hasattr(plugin, 'process_content'):
                    logger.debug(
                        "Processing content with plugin: %s",
                        plugin.metadata.name if hasattr(plugin, 'metadata') else plugin.__class__.__name__
                    )
                    content = plugin.process_content(content)

            context = {
                'content': content,
                'page_content': content,
                'page': page,
                'site': self.site,
                'url': page.url,
                'title': page.title,
                'date': page.date,
                'author': page.author,
                'category': page.category,
                'tags': page.tags,
                'metadata': page.metadata,
                'page_head_content': '',
                'static_url': self.config.get("static_url", "static"),
                'site_url': self.config.get("base_url", ""),
                'site_name': self.config.get("site_name", "StaticFlow Site")
            }

            for plugin in self.plugins:
                if hasattr(plugin, 'on_post_page'):
                    logger.debug(
                        "Processing page context with plugin: %s",
                        plugin.metadata.name if hasattr(plugin, 'metadata') else plugin.__class__.__name__
                    )
                    context = plugin.on_post_page(context)

            template = self.site.get_template(page.template)
            if template:
                logger.debug("Rendering page with template: %s", page.template)
                output = template.render(**context)
                self.site.save_page(page, output)
            else:
                logger.error("Template not found for page: %s", page.url)

        except Exception as e:
            logger.error("Error processing page %s: %s", page.url, e)

    def _copy_static_files(self) -> None:
        """Copy static files to output directory."""
        if not self.site.source_dir or not self.site.output_dir:
            logger.error(
                "Cannot copy static files: source_dir=%s, output_dir=%s",
                self.site.source_dir,
                self.site.output_dir
            )
            return

        static_dir = Path(self.site.config.get("static_dir", "static"))
        if not static_dir.exists():
            logger.error("Static directory does not exist: %s", static_dir)
            return

        logger.info(
            "Copying static files from %s to %s",
            static_dir,
            self.site.output_dir
        )

        try:
            for file_path in static_dir.rglob("*"):
                if file_path.is_file():
                    rel_path = file_path.relative_to(static_dir)
                    output_path = self.site.output_dir / "static" / rel_path
                    output_path.parent.mkdir(parents=True, exist_ok=True)

                    logger.info(
                        "Processing static file: %s -> %s",
                        file_path,
                        output_path
                    )

                    context = {
                        "file_path": str(file_path),
                        "output_path": str(output_path),
                        "relative_path": str(rel_path)
                    }

                    for plugin in self.plugins:
                        if hasattr(plugin, 'on_pre_asset'):
                            plugin_name = (
                                plugin.metadata.name if hasattr(plugin, 'metadata')
                                else plugin.__class__.__name__
                            )
                            logger.info(
                                "Running on_pre_asset hook for plugin %s on file %s",
                                plugin_name,
                                file_path
                            )
                            context = plugin.on_pre_asset(context)
                            if "content" in context:
                                logger.info(
                                    "Plugin %s modified content for file %s",
                                    plugin_name,
                                    file_path
                                )

                    if "content" in context:
                        logger.info(
                            "Writing modified content to %s",
                            output_path
                        )
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(context["content"])
                    else:
                        logger.info(
                            "Copying file %s to %s",
                            file_path,
                            output_path
                        )
                        shutil.copy2(file_path, output_path)

                    for plugin in self.plugins:
                        if hasattr(plugin, 'on_post_asset'):
                            plugin_name = (
                                plugin.metadata.name if hasattr(plugin, 'metadata')
                                else plugin.__class__.__name__
                            )
                            logger.info(
                                "Running on_post_asset hook for plugin %s on file %s",
                                plugin_name,
                                file_path
                            )
                            context = plugin.on_post_asset(context)
        except Exception as e:
            logger.error("Error copying static files: %s", e, exc_info=True)

    def clean(self) -> None:
        """Clean the build artifacts."""
        if self.site.output_dir and self.site.output_dir.exists():
            shutil.rmtree(self.site.output_dir)
        self._cache.clear()
        self.site.clear()

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

        content_html = self.markdown.convert(page.content)
        for plugin in self.plugins:
            content_html = plugin.process_content(content_html)

        head_content = []
        for plugin in self.plugins:
            if hasattr(plugin, 'get_head_content'):
                head_content.append(plugin.get_head_content())

        static_url = self.config.get("static_url", "static")

        if static_url.startswith('/') or static_url.startswith('http'):
            pass
        else:
            static_url = f"/{static_url}"

        static_url = static_url.rstrip('/')

        context = {
            "page": page,
            "site_name": self.config.get("site_name", "StaticFlow Site"),
            "site_url": self.config.get("base_url", ""),  
            "static_url": static_url,
            "page_content": content_html,
            "page_head_content": "\n".join(head_content) if head_content else "",
            "available_translations": {},
        }
        page.translations = {}

        from staticflow.templates.engine import TemplateEngine
        engine = TemplateEngine(template_dir)
        return engine.render(template_filename, context)
