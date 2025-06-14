from typing import Any, Dict, List, Optional
import markdown
from .base import ContentParser
from staticflow.plugins.syntax_highlight import SyntaxHighlightPlugin
from .extensions.video import makeExtension as makeVideoExtension
from .extensions.audio import makeExtension as makeAudioExtension


class MarkdownParser(ContentParser):
    """Парсер для Markdown контента."""

    def __init__(self, extensions: Optional[List[str]] = None):
        super().__init__()
        self.extensions = extensions or [
            'fenced_code',
            'tables',
            'toc',
            'meta',
            'attr_list',
            'def_list',
            'footnotes',
            'mdx_math',
            'pymdownx.highlight',
            'pymdownx.superfences',
            'pymdownx.arithmatex',
            'pymdownx.details',
            'pymdownx.emoji',
            'pymdownx.tasklist',
            'pymdownx.critic',
            'pymdownx.mark',
            'pymdownx.smartsymbols',
            'pymdownx.tabbed',
            'pymdownx.arithmatex',
            'pymdownx.betterem',
            'pymdownx.caret',
            'pymdownx.critic',
            'pymdownx.details',
            'pymdownx.emoji',
            'pymdownx.inlinehilite',
            'pymdownx.magiclink',
            'pymdownx.mark',
            'pymdownx.smartsymbols',
            'pymdownx.superfences',
            'pymdownx.tabbed',
            'pymdownx.tasklist',
            'pymdownx.tilde',
            makeVideoExtension(),
            makeAudioExtension(),
        ]
        self.extension_configs: Dict[str, Dict[str, Any]] = {
            'toc': {
                'permalink': True,
                'permalink_class': 'headerlink',
                'toc_depth': 3
            },
            'fenced_code': {
                'css_class': 'highlight'
            },
            'pymdownx.highlight': {
                'css_class': 'highlight',
                'guess_lang': True
            },
            'pymdownx.superfences': {
                'custom_fences': [
                    {
                        'name': 'mermaid',
                        'class': 'mermaid',
                        'format': str
                    }
                ]
            },
            'pymdownx.arithmatex': {
                'generic': True
            },
            'pymdownx.details': {
                'types': ['note', 'warning', 'danger', 'important', 'tip', 'attention']
            }
        }
        self._md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
        self.syntax_highlighter = SyntaxHighlightPlugin()

    def parse(self, content: str) -> str:
        """Преобразует Markdown в HTML."""
        self._md.reset()
        html = self._md.convert(content)

        if self.get_option('syntax_highlight'):
            html = self.syntax_highlighter.process_content(html)
            
        return html


    def add_extension(self, extension: str, config: Optional[Dict[str, Any]] = None) -> None:
        """Добавляет расширение Markdown."""
        if extension not in self.extensions:
            self.extensions.append(extension)
            if config:
                self.extension_configs[extension] = config
            self._md = markdown.Markdown(
                extensions=self.extensions,
                extension_configs=self.extension_configs
            )
