from typing import Dict, List
import re
from urllib.parse import urlparse
from bleach import clean
from bleach.sanitizer import ALLOWED_TAGS, ALLOWED_ATTRIBUTES


class ContentSecurity:
    """Система безопасности контента."""

    def __init__(self):
        self.allowed_tags = ALLOWED_TAGS.union({
            'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
            'pre', 'code', 'blockquote', 'img',
            'table', 'thead', 'tbody', 'tr', 'th', 'td'
        })

        self.allowed_attributes = ALLOWED_ATTRIBUTES.copy()
        self.allowed_attributes.update({
            'img': ['src', 'alt', 'title', 'width', 'height'],
            'a': ['href', 'title', 'rel'],
            'code': ['class'],
            'pre': ['class'],
            'table': ['class', 'width'],
            'th': ['scope'],
            'td': ['colspan', 'rowspan']
        })

        self.allowed_protocols = ['http', 'https', 'mailto', 'tel']
        self.allowed_styles = [
            'color', 'background-color', 'font-size', 'font-weight',
            'text-align', 'margin', 'padding', 'border'
        ]

    def sanitize_html(self, content: str) -> str:
        """Очищает HTML от потенциально опасного содержимого."""
        if not content:
            return ""
            
        # Очищаем HTML с помощью bleach
        cleaned = clean(
            content,
            tags=ALLOWED_TAGS,
            attributes=ALLOWED_ATTRIBUTES,
            strip=True
        )
        
        # Дополнительная очистка от JavaScript
        cleaned = re.sub(r'javascript:', '', cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r'alert\s*\([^)]*\)', '', cleaned, flags=re.IGNORECASE)
        
        return cleaned

    def validate_urls(self, content: str) -> List[str]:
        """Проверяет и валидирует все URL в контенте."""
        url_pattern = re.compile(
            r'(?:href|src)=["\']([^"\']+)["\']'
        )
        urls = url_pattern.findall(content)
        invalid_urls = []

        for url in urls:
            if not self.is_safe_url(url):
                invalid_urls.append(url)

        return invalid_urls

    def is_safe_url(self, url: str) -> bool:
        """Проверяет безопасность URL."""
        try:
            parsed = urlparse(url)
            return (
                parsed.scheme in self.allowed_protocols and
                not any(unsafe in url.lower() for unsafe in [
                    'javascript:', 'data:', 'vbscript:', 'file:'
                ])
            )
        except Exception:
            return False

    def sanitize_styles(self, content: str) -> str:
        """Очищает CSS стили от потенциально опасных значений."""
        style_pattern = re.compile(
            r'style=["\']([^"\']+)["\']'
        )

        def clean_style(match):
            styles = match.group(1)
            cleaned_styles = []
            
            for style in styles.split(';'):
                if ':' in style:
                    prop, value = style.split(':', 1)
                    prop = prop.strip().lower()
                    value = value.strip()
                    if prop in self.allowed_styles:
                        # Удаляем все URL и javascript из значений
                        has_url = 'url(' in value.lower()
                        has_js = 'javascript:' in value.lower()
                        if has_url or has_js:
                            continue
                        cleaned_styles.append(f"{prop}: {value}")
            
            if cleaned_styles:
                return f'style="{"; ".join(cleaned_styles)}"'
            return ''

        return style_pattern.sub(clean_style, content)

    def protect_against_xss(self, content: str) -> str:
        """Защищает контент от XSS-атак."""
        # Очистка HTML
        content = self.sanitize_html(content)
        
        # Валидация URL
        invalid_urls = self.validate_urls(content)
        for url in invalid_urls:
            content = content.replace(url, '#')
        
        # Очистка стилей
        content = self.sanitize_styles(content)
        
        return content

    def get_security_report(self, content: str) -> Dict[str, List[str]]:
        """Возвращает отчет о безопасности контента."""
        return {
            'invalid_urls': self.validate_urls(content),
            'sanitized_content': self.protect_against_xss(content)
        } 