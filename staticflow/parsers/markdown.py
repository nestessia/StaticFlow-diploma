from typing import Any, Dict, List, Optional, Union
import markdown
from .base import ContentParser
from staticflow.plugins.syntax_highlight import SyntaxHighlightPlugin
from .extensions.video import makeExtension as makeVideoExtension
from .extensions.audio import makeExtension as makeAudioExtension
from datetime import datetime
import frontmatter


class MarkdownParser(ContentParser):
    """Парсер для Markdown контента."""

    def __init__(
        self,
        extensions: Optional[List[Union[str, Any]]] = None
    ) -> None:
        super().__init__()
        self.extensions: List[Union[str, Any]] = extensions or [
            'fenced_code',
            'tables',
            'toc',
            'meta',
            'attr_list',
            'def_list',
            'footnotes',
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
        }
        self._md: markdown.Markdown = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
        self.syntax_highlighter: SyntaxHighlightPlugin = (
            SyntaxHighlightPlugin()
        )

    def parse(self, content: str) -> str:
        """Преобразует Markdown в HTML."""
        self._md.reset()
        html: str = self._md.convert(content)

        if self.get_option('syntax_highlight'):
            html = self.syntax_highlighter.process_content(html)

        return html

    def add_extension(
        self,
        extension: str,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Добавляет расширение Markdown."""
        if extension not in self.extensions:
            self.extensions.append(extension)
            if config:
                self.extension_configs[extension] = config
            self._md = markdown.Markdown(
                extensions=self.extensions,
                extension_configs=self.extension_configs
            )

    def validate(self, content: str) -> bool:
        """Валидирует Markdown контент."""
        if content is None:
            return False
        if not isinstance(content, str):
            return False
        if not content.strip():
            return False
        return True

    def get_metadata(self, content: str) -> Dict[str, Any]:
        """Получает метаданные из Markdown контента."""
        try:
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            
            # Преобразуем строковую дату в объект datetime
            if 'date' in metadata and isinstance(metadata['date'], str):
                try:
                    metadata['date'] = datetime.strptime(
                        metadata['date'], 
                        '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
                    
            return metadata
        except Exception:
            return {}
