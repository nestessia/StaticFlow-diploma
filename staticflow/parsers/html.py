from typing import Dict, Any
from bs4 import BeautifulSoup
from .base import ContentParser


class HTMLParser(ContentParser):
    """Парсер для HTML контента."""

    def __init__(self, beautify: bool = True):
        super().__init__()
        self.beautify = beautify

    def parse(self, content: str) -> str:
        """Обрабатывает HTML контент."""
        if not self.beautify:
            return content

        soup = BeautifulSoup(content, 'html.parser')
        html = soup.prettify()
        html = self.syntax_highlighter.process_content(html)
        return html

    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Извлекает метаданные из HTML-тегов meta."""
        soup = BeautifulSoup(content, 'html.parser')
        metadata = {}

        title_tag = soup.find('title')
        if title_tag:
            metadata['title'] = title_tag.string

        for meta in soup.find_all('meta'):
            name = meta.get('name')
            content = meta.get('content')
            if name and content:
                metadata[name] = content

        return metadata
