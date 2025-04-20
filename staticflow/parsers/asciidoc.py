from typing import Dict, Any
import asciidocapi
from .base import ContentParser


class AsciiDocParser(ContentParser):
    """Парсер для AsciiDoc контента."""
    
    def __init__(self):
        super().__init__()
        # Настройки AsciiDoc по умолчанию
        self.attributes = {
            'source-highlighter': 'pygments',
            'icons': 'font',
            'experimental': 'true',
            'sectlinks': 'true',
            'idprefix': '',
            'idseparator': '-'
        }
    
    def parse(self, content: str) -> str:
        """Преобразует AsciiDoc в HTML."""
        # Используем опции парсера, если они были установлены
        attributes = dict(self.attributes)
        
        # Добавляем кастомные атрибуты из опций
        custom_attrs = self.get_option('attributes', {})
        attributes.update(custom_attrs)
        
        # Создаем экземпляр AsciiDoc
        asciidoc = asciidocapi.AsciiDocAPI()
        
        # Устанавливаем атрибуты
        for key, value in attributes.items():
            asciidoc.attributes[key] = value
        
        # Опции безопасности
        safe_mode = self.get_option('safe_mode', 'safe')
        asciidoc.options.safe = safe_mode
        
        # Преобразуем в HTML
        html_output = ''
        asciidoc.convert(content, None, html_output)
        
        return html_output
    
    def parse_with_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Парсит контент с frontmatter и возвращает метаданные и содержимое."""
        # Используем реализацию базового класса для frontmatter
        metadata, content = super().parse_with_frontmatter(content)
        
        # Если метаданные пустые, попробуем извлечь их из заголовка AsciiDoc
        if not metadata:
            metadata = self._extract_metadata_from_header(content)
            
        return metadata, self.parse(content)
    
    def _extract_metadata_from_header(self, content: str) -> Dict[str, Any]:
        """Извлекает метаданные из заголовка AsciiDoc документа."""
        metadata = {}
        lines = content.split('\n')
        
        # Ищем метаданные в формате: `:key: value`
        for line in lines:
            if line.startswith(':') and ':' in line[1:]:
                parts = line[1:].split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    metadata[key] = value
            # Прекращаем поиск, если находим новый раздел
            elif line.startswith('=') or not line.strip():
                break
                
        # Пытаемся получить заголовок
        for line in lines:
            if line.startswith('= '):
                metadata['title'] = line[2:].strip()
                break
                
        return metadata
    
    def set_attribute(self, key: str, value: str) -> None:
        """Устанавливает атрибут AsciiDoc."""
        self.attributes[key] = value
    
    def update_attributes(self, attributes: Dict[str, str]) -> None:
        """Обновляет атрибуты AsciiDoc."""
        self.attributes.update(attributes) 