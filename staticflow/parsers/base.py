from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List
import frontmatter


class ContentParser(ABC):
    """Базовый класс для парсеров контента."""

    def __init__(self):
        self.options: Dict[str, Any] = {
            'syntax_highlight': True,
            'math_support': True,
            'toc': True,
            'callouts': True,
            'tables': True,
            'footnotes': True,
            'code_blocks': True,
            'smart_quotes': True,
            'link_anchors': True,
            'image_processing': True,
            'diagrams': True
        }
        self.extensions: List[str] = []

    @abstractmethod
    def parse(self, content: str) -> str:
        """Преобразует исходный контент в HTML."""
        pass

    def parse_with_frontmatter(self, content: str) -> tuple[Dict[str, Any], str]:
        """Парсит контент с frontmatter и возвращает метаданные и содержимое."""
        post = frontmatter.loads(content)
        metadata = dict(post.metadata)
        return metadata, self.parse(post.content)

    def set_option(self, key: str, value: Any) -> None:
        """Устанавливает опцию парсера."""
        self.options[key] = value

    def get_option(self, key: str, default: Any = None) -> Any:
        """Получает значение опции парсера."""
        return self.options.get(key, default)

    def enable_extension(self, extension: str) -> None:
        """Включает расширение парсера."""
        if extension not in self.extensions:
            self.extensions.append(extension)

    def disable_extension(self, extension: str) -> None:
        """Отключает расширение парсера."""
        if extension in self.extensions:
            self.extensions.remove(extension)

    def has_extension(self, extension: str) -> bool:
        """Проверяет наличие расширения."""
        return extension in self.extensions 