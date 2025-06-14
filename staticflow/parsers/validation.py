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
        self._current_content: str = ""

    def validate_structure(self, content: str) -> bool:
        """Валидирует структуру HTML."""
        if not content:
            return True
            
        self.errors = []
        self._current_content = content
        
        # Проверяем баланс тегов
        tag_pattern = re.compile(r'<([^>]+)>')
        tags = tag_pattern.findall(content)
        stack = []

        for tag in tags:
            if tag.startswith('/'):
                if not stack:
                    msg = f"Обнаружен закрывающий тег {tag} без открывающего"
                    self.add_error(msg, content.find(tag))
                    return False
                if stack[-1] != tag[1:]:
                    msg = (
                        f"Некорректная вложенность тегов: "
                        f"{stack[-1]} и {tag}"
                    )
                    self.add_error(msg, content.find(tag))
                    return False
                stack.pop()
            elif not tag.endswith('/'):
                stack.append(tag)

        if stack:
            msg = f"Обнаружены незакрытые теги: {', '.join(stack)}"
            self.add_error(msg, content.find(stack[-1]))
            return False
            
        # Проверяем наличие JavaScript
        js_pattern = re.compile(r'javascript:', re.IGNORECASE)
        js_match = js_pattern.search(content)
        if js_match:
            self.add_error("Обнаружен JavaScript в контенте", js_match.start())
            
        # Проверяем наличие скриптов
        script_pattern = re.compile(r'<script[^>]*>.*?</script>', re.DOTALL | re.IGNORECASE)
        script_match = script_pattern.search(content)
        if script_match:
            self.add_error("Обнаружен тег script", script_match.start())
            
        # Проверяем наличие iframe
        iframe_pattern = re.compile(r'<iframe[^>]*>.*?</iframe>', re.DOTALL | re.IGNORECASE)
        iframe_match = iframe_pattern.search(content)
        if iframe_match:
            self.add_error("Обнаружен тег iframe", iframe_match.start())
            
        return len(self.errors) == 0

    def validate_attributes(self, content: str) -> bool:
        """Валидирует атрибуты HTML тегов."""
        if not content:
            return True
            
        self.errors = []
        self._current_content = content
        
        # Проверяем JavaScript в атрибутах
        js_pattern = re.compile(r'javascript:', re.IGNORECASE)
        js_match = js_pattern.search(content)
        if js_match:
            self.add_error("Обнаружен JavaScript в атрибутах", js_match.start())
            
        # Проверяем URL в атрибутах
        url_pattern = re.compile(r'href=["\'](?!https?://)[^"\']+["\']')
        url_match = url_pattern.search(content)
        if url_match:
            self.add_error("Обнаружены некорректные URL в атрибутах", url_match.start())
            
        return len(self.errors) == 0

    def validate_nesting(self, content: str) -> bool:
        """Валидирует вложенность HTML тегов."""
        if not content:
            return True
            
        self.errors = []
        
        # Проверяем корректность вложенности
        stack = []
        pattern = re.compile(r'<(/?)([a-zA-Z0-9]+)[^>]*>')
        
        for match in pattern.finditer(content):
            is_closing = bool(match.group(1))
            tag = match.group(2).lower()
            
            if not is_closing:
                stack.append(tag)
            else:
                if not stack:
                    self.errors.append(f"Обнаружен закрывающий тег {tag} без открывающего")
                elif stack[-1] != tag:
                    self.errors.append(f"Некорректная вложенность тегов: {stack[-1]} и {tag}")
                else:
                    stack.pop()
                    
        if stack:
            self.errors.append(f"Обнаружены незакрытые теги: {', '.join(stack)}")
            
        return len(self.errors) == 0

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
        return self._current_content[:position].count('\n') + 1

    def get_column_number(self, position: int) -> int:
        """Вычисляет номер колонки для позиции в тексте."""
        last_newline = self._current_content[:position].rfind('\n')
        return position - last_newline if last_newline != -1 else position + 1

    def get_validation_report(self) -> Dict[str, Any]:
        """Возвращает отчет о валидации."""
        return {
            "is_valid": len(self.errors) == 0,
            "errors": self.errors,
            "warnings": self.warnings,
            "content": self._current_content
        } 