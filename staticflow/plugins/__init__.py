from .core.base import Plugin, PluginMetadata, HookType
from .core.manager import PluginManager
from .builtin import SEOPlugin, SitemapPlugin, RSSPlugin, MinifierPlugin
from .syntax_highlight import SyntaxHighlightPlugin
from .math import MathPlugin
from .diagrams import MermaidPlugin
from .notion_blocks import NotionBlocksPlugin

__all__ = [
    'Plugin',
    'PluginMetadata',
    'HookType',
    'PluginManager',
    'SEOPlugin',
    'SitemapPlugin',
    'RSSPlugin',
    'MinifierPlugin'
]

def initialize_plugins(engine) -> None:
    """Initialize all plugins for the engine."""
    engine.add_plugin(SyntaxHighlightPlugin())
    engine.add_plugin(MathPlugin())
    engine.add_plugin(MermaidPlugin())
    engine.add_plugin(NotionBlocksPlugin()) 