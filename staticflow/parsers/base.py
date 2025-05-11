from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import frontmatter


class ContentParser(ABC):
    """Базовый класс для парсеров контента."""

    def __init__(self):
        self.options: Dict[str, Any] = {}

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