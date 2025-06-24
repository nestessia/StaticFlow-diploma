from .core.base import Plugin, PluginMetadata, HookType
from .core.manager import PluginManager
from .builtin import SEOPlugin, SitemapPlugin, RSSPlugin, MinifierPlugin
from .syntax_highlight import SyntaxHighlightPlugin
from .math import MathPlugin
from .diagrams import MermaidPlugin
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
        "minifier": {
            "enabled": True,
            "minify_html": True,
            "minify_css": True,
            "minify_js": True,
            "preserve_comments": False
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
    enabled_plugins = engine.config.get("PLUGINS", {}).get("enabled", [])

    # Initialize syntax highlighting plugin
    if "syntax_highlight" in enabled_plugins:
        syntax_plugin = SyntaxHighlightPlugin()
        engine.add_plugin(syntax_plugin, default_configs.get("syntax_highlight"))

    # Initialize math plugin
    if "math" in enabled_plugins:
        math_plugin = MathPlugin()
        engine.add_plugin(math_plugin, default_configs.get("math"))

    # Initialize diagrams plugin
    if "diagrams" in enabled_plugins:
        diagrams_plugin = MermaidPlugin()
        engine.add_plugin(diagrams_plugin, default_configs.get("diagrams"))

    # Initialize media plugin
    if "media" in enabled_plugins:
        media_plugin = MediaPlugin()
        engine.add_plugin(media_plugin, default_configs.get("media"))

    # Initialize minifier plugin
    if "minifier" in enabled_plugins:
        minifier_config = engine.config.get("PLUGIN_MINIFIER", {})
        minifier_plugin = MinifierPlugin()
        config = {
            **default_configs.get("minifier"),
            **minifier_config
        }
        engine.add_plugin(minifier_plugin, config)

    # Initialize SEO plugin
    if "seo" in enabled_plugins:
        seo_plugin = SEOPlugin()
        engine.add_plugin(seo_plugin)

    # Initialize CDN plugin
    if "cdn" in enabled_plugins:
        cdn_config = engine.config.get("PLUGIN_CDN", {})
        cdn_plugin = CDNPlugin()
        config = {
            **default_configs.get("cdn"),
            **cdn_config
        }
        engine.add_plugin(cdn_plugin, config)

    base_url = engine.config.get("base_url")
    if base_url:
        if isinstance(base_url, Path):
            base_url = str(base_url)

        # Initialize sitemap plugin if enabled
        if "sitemap" in enabled_plugins:
            sitemap_config = {
                "base_url": base_url,
                "output_path": engine.config.get("output_dir")
            }
            sitemap_plugin = SitemapPlugin()
            engine.add_plugin(sitemap_plugin, sitemap_config)

        # Initialize RSS plugin if enabled
        if "rss" in enabled_plugins:
            rss_config = {
                "site_name": engine.config.get("site_name", "StaticFlow Site"),
                "site_description": engine.config.get("description", ""),
                "base_url": base_url,
                "output_path": engine.config.get("output_dir"),
                "language": engine.config.get("language", "en")
            }
            rss_plugin = RSSPlugin()
            engine.add_plugin(rss_plugin, rss_config)
