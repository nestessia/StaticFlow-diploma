from typing import Any, Dict, Optional
from docutils.core import publish_parts
from .base import ContentParser
import re
from staticflow.plugins.syntax_highlight import SyntaxHighlightPlugin


class RSTParser(ContentParser):
    """Парсер для reStructuredText контента."""

    def __init__(self, settings: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.settings = settings or {
            'initial_header_level': 2,
            'doctitle_xform': True,
            'sectsubtitle_xform': True,
            'embed_stylesheet': False,
            'stylesheet_path': None,
            'math_output': 'MathJax',
            'smart_quotes': True,
            'halt_level': 2,
            'report_level': 1,
            'exit_status_level': 2,
            'syntax_highlight': 'short',
            'highlight_language': 'python',
            'input_encoding': 'utf-8',
            'output_encoding': 'utf-8',
        }
        self.syntax_highlighter = SyntaxHighlightPlugin()

    def parse(self, content: str) -> str:
        """Преобразует reStructuredText в HTML."""
        parts = publish_parts(
            source=content,
            writer_name='html',
            settings_overrides=self.settings
        )
        html = parts['html_body']

        # Преобразуем admonition в callout Notion-style
        def admonition_to_callout(match):
            type_map = {
                'note': ('info', 'ℹ️'),
                'warning': ('warning', '⚠️'),
                'danger': ('error', '⛔'),
                'important': ('important', '❗'),
                'tip': ('tip', '💡'),
                'attention': ('attention', '👀'),
            }
            ad_type = match.group(1).lower()
            notion_type, icon = type_map.get(ad_type, ('info', 'ℹ️'))
            title = match.group(2)
            content = match.group(3)
            return (
                f'<div class="callout {notion_type}">'
                f'<div class="callout-icon">{icon}</div>'
                f'<div class="callout-content"><strong>{title}</strong> {content.strip()}</div>'
                f'</div>'
            )

        # Регулярка для поиска admonition-блоков
        html = re.sub(
            r'<div class="admonition (\w+)">.*?<p class="first admonition-title">(.*?)</p>(.*?)</div>',
            admonition_to_callout,
            html,
            flags=re.DOTALL
        )
        html = self.syntax_highlighter.process_content(html)
        return html

    def set_setting(self, key: str, value: Any) -> None:
        """Устанавливает настройку парсера RST."""
        self.settings[key] = value
        self.options[key] = value  # Для совместимости с базовым классом 