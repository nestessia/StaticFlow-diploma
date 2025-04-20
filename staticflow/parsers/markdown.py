from typing import Any, Dict, List, Optional
import markdown
from .base import ContentParser


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
            'footnotes'
        ]
        self.extension_configs: Dict[str, Dict[str, Any]] = {
            'toc': {
                'permalink': True,
                'permalink_class': 'headerlink'
            },
            'fenced_code': {
                'css_class': 'highlight'
            }
        }
        self._md = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs
        )
    
    def parse(self, content: str) -> str:
        """Преобразует Markdown в HTML."""
        # Сбрасываем состояние парсера перед каждым использованием
        self._md.reset()
        return self._md.convert(content)
    
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