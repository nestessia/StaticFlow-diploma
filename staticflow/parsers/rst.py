from typing import Dict, Any
from docutils.core import publish_parts
from docutils.parsers.rst.directives import register_directive
from .base import ContentParser


class RSTParser(ContentParser):
    """Парсер для reStructuredText контента."""
    
    def __init__(self):
        super().__init__()
        self.writer_name = 'html5'
        self.settings = {
            'initial_header_level': 1,
            'syntax_highlight': 'short',
            'embed_stylesheet': False,
            'doctitle_xform': False,
            'sectsubtitle_xform': False,
        }
    
    def parse(self, content: str) -> str:
        """Преобразует reStructuredText в HTML."""
        parts = publish_parts(
            source=content,
            writer_name=self.writer_name,
            settings_overrides=self.settings
        )
        return parts['html_body']
    
    def parse_with_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Парсит контент с frontmatter и возвращает метаданные и содержимое."""
        # Сначала пробуем обработать как обычный frontmatter
        metadata, content = super().parse_with_frontmatter(content)
        
        # Если метаданные пустые, пробуем извлечь их из RST
        if not metadata:
            opts = self.settings
            parts = publish_parts(
                source=content,
                writer=self.writer_name,
                settings_overrides=opts
            )
            # Извлекаем метаданные из docinfo
            if 'docinfo' in parts:
                metadata = self._parse_docinfo(parts['docinfo'])
            # Используем заголовок как title
            # если он не задан
            if 'title' in parts and not metadata.get('title'):
                metadata['title'] = parts['title']
        
        return metadata, self.parse(content)
    
    def _parse_docinfo(self, docinfo: str) -> Dict[str, Any]:
        """Парсит docinfo из RST в словарь метаданных."""
        metadata = {}
        if not docinfo:
            return metadata
            
        # Простой парсинг docinfo таблицы
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(docinfo, 'html.parser')
        
        for field in soup.find_all('tr', class_='field'):
            name = field.find(class_='field-name')
            body = field.find(class_='field-body')
            if name and body:
                key = name.text.lower().replace(':', '').strip()
                value = body.text.strip()
                metadata[key] = value
                
        return metadata
    
    def add_directive(self, name: str, directive_class: type) -> None:
        """Регистрирует новую RST директиву."""
        register_directive(name, directive_class)
    
    def set_writer_name(self, writer_name: str) -> None:
        """Устанавливает имя writer'а для docutils."""
        self.writer_name = writer_name
    
    def update_settings(self, settings: Dict[str, Any]) -> None:
        """Обновляет настройки docutils."""
        self.settings.update(settings) 