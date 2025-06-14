from typing import Any, Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import re


class ValidationLevel(Enum):
    STRICT = "strict"
    NORMAL = "normal"
    RELAXED = "relaxed"


@dataclass
class ValidationError:
    message: str
    line: int
    column: int
    level: ValidationLevel
    context: Optional[str] = None


class ContentValidator:
    """Система валидации контента."""

    def __init__(self, level: ValidationLevel = ValidationLevel.NORMAL):
        self.level = level
        self.errors: List[ValidationError] = []
        self.warnings: List[ValidationError] = []

    def validate_structure(self, content: str) -> bool:
        """Проверяет структуру контента."""
        # Проверка баланса тегов
        tag_pattern = re.compile(r'<([^>]+)>')
        tags = tag_pattern.findall(content)
        stack = []

        for i, tag in enumerate(tags):
            if tag.startswith('/'):
                if not stack:
                    self.add_error(f"Незакрытый тег {tag}", i)
                    return False
                if stack[-1] != tag[1:]:
                    self.add_error(f"Несоответствие тегов: {stack[-1]} и {tag}", i)
                    return False
                stack.pop()
            elif not tag.endswith('/'):
                stack.append(tag)

        if stack:
            self.add_error(f"Незакрытые теги: {', '.join(stack)}", len(tags))
            return False

        return True

    def validate_attributes(self, content: str) -> bool:
        """Проверяет атрибуты элементов."""
        # Проверка URL в атрибутах
        url_pattern = re.compile(r'(?:href|src)=["\']([^"\']+)["\']')
        urls = url_pattern.findall(content)

        for url in urls:
            if not self.is_valid_url(url):
                self.add_error(f"Некорректный URL: {url}", content.find(url))

        # Проверка стилевых атрибутов
        style_pattern = re.compile(r'style=["\']([^"\']+)["\']')
        styles = style_pattern.findall(content)

        for style in styles:
            if not self.is_valid_style(style):
                self.add_error(f"Некорректный стиль: {style}", content.find(style))

        return len(self.errors) == 0

    def validate_nesting(self, content: str) -> bool:
        """Проверяет правильность вложенности элементов."""
        # Проверка вложенности блочных элементов
        block_elements = ['div', 'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'ul', 'ol', 'li']
        for element in block_elements:
            pattern = re.compile(f'<{element}[^>]*>.*?<{element}[^>]*>', re.DOTALL)
            if pattern.search(content):
                self.add_error(f"Неправильная вложенность элемента {element}", 0)
                return False

        return True

    def is_valid_url(self, url: str) -> bool:
        """Проверяет корректность URL."""
        url_pattern = re.compile(
            r'^(?:http|https)://'  # http:// или https://
            r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # домен
            r'localhost|'  # localhost
            r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # IP
            r'(?::\d+)?'  # порт
            r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return bool(url_pattern.match(url))

    def is_valid_style(self, style: str) -> bool:
        """Проверяет корректность CSS стилей."""
        # Базовые проверки CSS
        if 'javascript:' in style.lower():
            return False
        if 'expression(' in style.lower():
            return False
        return True

    def add_error(self, message: str, position: int, level: ValidationLevel = None) -> None:
        """Добавляет ошибку валидации."""
        if level is None:
            level = self.level

        error = ValidationError(
            message=message,
            line=self.get_line_number(position),
            column=self.get_column_number(position),
            level=level
        )

        if level == ValidationLevel.STRICT:
            self.errors.append(error)
        else:
            self.warnings.append(error)

    def get_line_number(self, position: int) -> int:
        """Вычисляет номер строки для позиции в тексте."""
        return content[:position].count('\n') + 1

    def get_column_number(self, position: int) -> int:
        """Вычисляет номер колонки для позиции в тексте."""
        last_newline = content[:position].rfind('\n')
        return position - last_newline if last_newline != -1 else position + 1

    def get_validation_report(self) -> Dict[str, List[ValidationError]]:
        """Возвращает отчет о валидации."""
        return {
            'errors': self.errors,
            'warnings': self.warnings
        } 