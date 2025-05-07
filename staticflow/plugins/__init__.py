from .core.base import Plugin, PluginMetadata, HookType
from .core.manager import PluginManager
from .builtin import SEOPlugin, SitemapPlugin, RSSPlugin, MinifierPlugin
from .syntax_highlight import SyntaxHighlightPlugin
from .math import MathPlugin
from .diagrams import MermaidPlugin
from .notion_blocks import NotionBlocksPlugin
from pathlib import Path

__all__ = [
    'Plugin',
    'PluginMetadata',
    'HookType',
    'PluginManager',
    'SEOPlugin',
    'SitemapPlugin',
    'RSSPlugin',
    'MinifierPlugin',
    'get_default_plugin_configs',
    'initialize_plugins'
]


def get_default_plugin_configs():
    """Get default configurations for all built-in plugins."""
    return {
        "syntax_highlight": {
            "style": "monokai",
            "linenums": False,
            "css_class": "highlight",
            "tabsize": 4,
            "preserve_tabs": True
        },
        "math": {
            "auto_render": True
        },
        "diagrams": {
            "theme": "default"
        },
        "notion_blocks": {
            "enabled": True
        }
    }


def initialize_plugins(engine) -> None:
    """Initialize all plugins for the engine with default configurations."""
    default_configs = get_default_plugin_configs()
    
    # Initialize syntax highlighting plugin
    syntax_plugin = SyntaxHighlightPlugin()
    engine.add_plugin(syntax_plugin, default_configs.get("syntax_highlight"))
    
    # Initialize math plugin
    math_plugin = MathPlugin()
    engine.add_plugin(math_plugin, default_configs.get("math"))
    
    # Initialize diagrams plugin
    diagrams_plugin = MermaidPlugin()
    engine.add_plugin(diagrams_plugin, default_configs.get("diagrams"))
    
    # Initialize notion blocks plugin
    notion_plugin = NotionBlocksPlugin()
    engine.add_plugin(notion_plugin, default_configs.get("notion_blocks"))
    
    # Initialize minifier plugin
    minifier_plugin = MinifierPlugin()
    engine.add_plugin(minifier_plugin)
    
    # Initialize SEO plugin
    seo_plugin = SEOPlugin()
    engine.add_plugin(seo_plugin)
    
    # Инициализируем плагины для работы с base_url
    # только если базовый URL сконфигурирован
    base_url = engine.config.get("base_url")
    if base_url:
        # Используем безопасное преобразование к строке
        if isinstance(base_url, Path):
            base_url = str(base_url)
        
        # Sitemap plugin
        sitemap_config = {
            "base_url": base_url,
            "output_path": engine.config.get("output_dir", "public")
        }
        sitemap_plugin = SitemapPlugin()
        engine.add_plugin(sitemap_plugin, sitemap_config)
        
        # RSS plugin
        rss_config = {
            "site_name": engine.config.get("site_name", "StaticFlow Site"),
            "site_description": engine.config.get("description", ""),
            "base_url": base_url,
            "output_path": engine.config.get("output_dir", "public"),
            "language": engine.config.get("language", "en")
        }
        rss_plugin = RSSPlugin()
        engine.add_plugin(rss_plugin, rss_config) 