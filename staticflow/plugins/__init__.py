from .core.base import Plugin, PluginMetadata, HookType
from .core.manager import PluginManager
from .builtin import SEOPlugin, SitemapPlugin, RSSPlugin, MinifierPlugin
from .syntax_highlight import SyntaxHighlightPlugin
from .math import MathPlugin
from .diagrams import MermaidPlugin
from .notion_blocks import NotionBlocksPlugin
from .media import MediaPlugin
from .cdn import CDNPlugin
from .multilingual import MultilingualPlugin
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
    'MediaPlugin',
    'CDNPlugin',
    'MultilingualPlugin',
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
        },
        "media": {
            "output_dir": "media",
            "source_dir": "static",
            "sizes": {
                "thumbnail": {"width": 200, "height": 200, "quality": 70},
                "small": {"width": 400, "quality": 80},
                "medium": {"width": 800, "quality": 85},
                "large": {"width": 1200, "quality": 90},
                "original": {"quality": 95}
            },
            "formats": ["webp", "original"],
            "generate_placeholders": True,
            "placeholder_size": 20,
            "process_videos": True,
            "video_thumbnail": True,
            "hash_filenames": True,
            "hash_length": 8
        },
        "cdn": {
            "enabled": True,
            "provider": "cloudflare",
            "api_token": "${CLOUDFLARE_API_TOKEN}",
            "zone_id": "${CLOUDFLARE_ZONE_ID}",
            "account_id": "${CLOUDFLARE_ACCOUNT_ID}",
            "domain": "cdn.example.com",
            "bucket": "staticflow-assets"
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
    
    # Initialize media plugin
    media_plugin = MediaPlugin()
    engine.add_plugin(media_plugin, default_configs.get("media"))
    
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