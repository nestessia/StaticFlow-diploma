from pathlib import Path
import shutil
import markdown
from typing import List, Optional, Dict, Any
from .config import Config
from .site import Site
from .page import Page
from ..plugins.base import Plugin
import pycountry


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
        
        # Инициализируем i18n
        from ..utils.i18n import get_i18n
        self.i18n = get_i18n()
        self.i18n.configure(self.config.config)
        
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
        
        # Получаем текущий язык страницы
        language = page.metadata.get("language", self.config.get("language", "ru"))
        
        # Проверяем наличие локализованной версии шаблона только для многоязычных сайтов
        if self.i18n.is_multilingual:
            lang_template_path = template_dir / language / template_filename
            template_path = lang_template_path if lang_template_path.exists() else template_dir / template_filename
        else:
            # Для моноязычных сайтов используем стандартный путь к шаблону
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

        # Загружаем переводы для текущего языка только для многоязычных сайтов
        if self.i18n.is_multilingual:
            translations_dir = Path("static/i18n")
            if translations_dir.exists():
                self.i18n.load_translations(translations_dir)
        
        # Get available languages and URLs for language switcher
        languages = []
        base_url = self.config.get("base_url", "")
        current_lang = language
        
        # Получаем языки из i18n, т.к. он уже правильно обработал конфигурацию
        if self.i18n.is_multilingual and self.i18n.languages:
            for lang_code in self.i18n.languages:
                # Create language entry
                try:
                    lang_obj = pycountry.languages.get(alpha_2=lang_code)
                    if lang_obj:
                        lang_name = lang_obj.name if lang_code != current_lang else f"[{lang_obj.name}]"
                    else:
                        lang_name = lang_code.upper() if lang_code != current_lang else f"[{lang_code.upper()}]"
                except Exception as e:
                    # Если не удалось получить название языка, используем код и логируем ошибку
                    print(f"Error getting language name for {lang_code}: {e}")
                    lang_name = lang_code.upper() if lang_code != current_lang else f"[{lang_code.upper()}]"
                    
                lang_url = f"{base_url}/{lang_code}" if lang_code != self.config.get("language") else base_url
                languages.append({
                    "code": lang_code,
                    "name": lang_name,
                    "url": lang_url
                })
        
        # Prepare template variables
        template_vars = {
            "page": {
                "title": page.title,
                "content": content_html,
                "language": current_lang,
                "head_content": "\n".join(head_content) if head_content else "",
                "url": page.get_url(base_url),
                "metadata": page.metadata
            },
            "site": {
                "title": self.config.get_nested(["languages", current_lang, "site_name"]) 
                    if self.i18n.is_multilingual else self.config.get("site_name", ""),
                "description": self.config.get_nested(["languages", current_lang, "description"]) 
                    if self.i18n.is_multilingual else self.config.get("description", ""),
                "author": self.config.get("author", ""),
                "base_url": base_url
            },
            "i18n": self.i18n.translations.get(current_lang, {}),
            "language_prefix": self.i18n.get_url_prefix(current_lang),
            "languages": languages
        }
        
        # Simple template rendering
        html = template_content
        
        # Replace variables in the template
        for var_name, var_value in template_vars.items():
            if isinstance(var_value, dict):
                for sub_name, sub_value in var_value.items():
                    html = html.replace(f"{{ {var_name}.{sub_name} }}", str(sub_value))
            else:
                html = html.replace(f"{{ {var_name} }}", str(var_value))
        
        # Обработка условий {% if ... %}
        # Примитивная реализация, для полноценного шаблонизатора нужно использовать Jinja2 или другой
        import re
        
        # Обработка {% if languages %}...{% endif %}
        if languages:
            html = re.sub(r'{%\s*if\s+languages\s*%}(.*?){%\s*endif\s*%}', r'\1', html, flags=re.DOTALL)
        else:
            html = re.sub(r'{%\s*if\s+languages\s*%}(.*?){%\s*endif\s*%}', '', html, flags=re.DOTALL)
        
        # Обработка {% for lang in languages %}...{% endfor %}
        def replace_for_loop(match):
            loop_content = match.group(1)
            result = ""
            
            for lang in languages:
                item_content = loop_content
                # Заменяем {{ lang.url }}
                item_content = item_content.replace("{{ lang.url }}", lang["url"])
                # Заменяем {{ lang.code }}
                item_content = item_content.replace("{{ lang.code }}", lang["code"])
                # Заменяем {{ lang.name }}
                item_content = item_content.replace("{{ lang.name }}", lang["name"])
                # Обработка условий в цикле {% if lang.code == page.language %}...{% endif %}
                if lang["code"] == current_lang:
                    item_content = re.sub(r'{%\s*if\s+lang\.code\s*==\s*page\.language\s*%}(.*?){%\s*endif\s*%}', r'\1', item_content, flags=re.DOTALL)
                else:
                    item_content = re.sub(r'{%\s*if\s+lang\.code\s*==\s*page\.language\s*%}(.*?){%\s*endif\s*%}', '', item_content, flags=re.DOTALL)
                
                result += item_content
                
            return result
        
        html = re.sub(r'{%\s*for\s+lang\s+in\s+languages\s*%}(.*?){%\s*endfor\s*%}', replace_for_loop, html, flags=re.DOTALL)

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