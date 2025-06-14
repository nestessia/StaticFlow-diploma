from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, List, Tuple
import frontmatter
from .validation import ContentValidator, ValidationLevel
from .security import ContentSecurity
from .cache import ParserCache


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
            'diagrams': True,
            'validation_level': ValidationLevel.NORMAL,
            'cache_ttl': 3600,
            'enable_cache': True,
            'enable_security': True
        }
        self.extensions: List[str] = []
        self.validator = ContentValidator()
        self.security = ContentSecurity()
        self.cache = ParserCache()

    @abstractmethod
    def parse(self, content: str) -> str:
        """Преобразует исходный контент в HTML."""
        pass

    def parse_with_frontmatter(self, content: str) -> Tuple[Dict[str, Any], str]:
        """Парсит контент с frontmatter и возвращает метаданные и содержимое."""
        post = frontmatter.loads(content)
        metadata = dict(post.metadata)
        
        # Проверка кэша
        if self.options['enable_cache']:
            cached_result = self.cache.get(post.content, self.options)
            if cached_result is not None:
                return metadata, cached_result

        # Валидация контента
        if self.options['enable_security']:
            validation_report = self.validator.validate_structure(post.content)
            if not validation_report:
                raise ValueError("Validation failed")

        # Парсинг контента
        parsed_content = self.parse(post.content)

        # Применение безопасности
        if self.options['enable_security']:
            parsed_content = self.security.protect_against_xss(parsed_content)

        # Кэширование результата
        if self.options['enable_cache']:
            self.cache.set(
                post.content,
                self.options,
                parsed_content,
                self.options['cache_ttl']
            )

        return metadata, parsed_content

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

    def get_validation_report(self, content: str) -> Dict[str, Any]:
        """Возвращает отчет о валидации контента."""
        return self.validator.get_validation_report()

    def get_security_report(self, content: str) -> Dict[str, Any]:
        """Возвращает отчет о безопасности контента."""
        return self.security.get_security_report(content)

    def get_cache_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша."""
        return self.cache.get_stats()

    def invalidate_cache(self, key: Optional[str] = None) -> None:
        """Инвалидирует кэш."""
        self.cache.invalidate(key) 