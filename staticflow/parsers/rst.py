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
            'toc_depth': 3,
            'toc_backlinks': 'entry',
            'toc_include_backlinks': True,
            'toc_include_hidden': False,
            'toc_include_orphans': True,
            'toc_include_titles': True,
            'toc_include_links': True,
            'toc_include_anchors': True,
            'toc_include_headers': True,
            'toc_include_sections': True,
            'toc_include_subsections': True,
            'toc_include_paragraphs': False,
            'toc_include_figures': True,
            'toc_include_tables': True,
            'toc_include_code_blocks': True,
            'toc_include_lists': True,
            'toc_include_definition_lists': True,
            'toc_include_field_lists': True,
            'toc_include_option_lists': True,
            'toc_include_quoted_lists': True,
            'toc_include_enumerated_lists': True,
            'toc_include_bullet_lists': True,
            'toc_include_definition_terms': True,
            'toc_include_definition_definitions': True,
            'toc_include_field_names': True,
            'toc_include_field_bodies': True,
            'toc_include_option_names': True,
            'toc_include_option_arguments': True,
            'toc_include_option_descriptions': True,
            'toc_include_quoted_paragraphs': True,
            'toc_include_doctest_blocks': True,
            'toc_include_raw_blocks': True,
            'toc_include_literal_blocks': True,
            'toc_include_line_blocks': True,
            'toc_include_block_quotes': True,
            'toc_include_attribution': True,
            'toc_include_epigraphs': True,
            'toc_include_highlights': True,
            'toc_include_pull_quotes': True,
            'toc_include_compound_paragraphs': True,
            'toc_include_container': True,
            'toc_include_decoration': True,
            'toc_include_header': True,
            'toc_include_footer': True,
            'toc_include_sidebar': True,
            'toc_include_topic': True,
            'toc_include_rubric': True,
            'toc_include_compound': True,
            'toc_include_attention': True,
            'toc_include_caution': True,
            'toc_include_danger': True,
            'toc_include_error': True,
            'toc_include_hint': True,
            'toc_include_important': True,
            'toc_include_note': True,
            'toc_include_tip': True,
            'toc_include_warning': True,
            'toc_include_admonition': True,
            'toc_include_image': True,
            'toc_include_figure': True,
            'toc_include_table': True,
            'toc_include_code': True,
            'toc_include_math': True,
            'toc_include_raw': True,
            'toc_include_include': True,
            'toc_include_role': True,
            'toc_include_class': True,
            'toc_include_name': True,
            'toc_include_id': True,
            'toc_include_ref': True,
            'toc_include_index': True,
            'toc_include_glossary': True,
            'toc_include_acronym': True,
            'toc_include_citation': True,
            'toc_include_target': True,
            'toc_include_substitution': True,
            'toc_include_footnote': True,
            'toc_include_citation': True,
            'toc_include_reference': True,
            'toc_include_hyperlink': True,
            'toc_include_anonymous': True,
            'toc_include_uri': True,
            'toc_include_email': True,
            'toc_include_tel': True,
            'toc_include_manpage': True,
            'toc_include_rfc': True,
            'toc_include_pep': True,
            'toc_include_rst': True,
            'toc_include_math': True,
            'toc_include_raw': True,
            'toc_include_include': True,
            'toc_include_role': True,
            'toc_include_class': True,
            'toc_include_name': True,
            'toc_include_id': True,
            'toc_include_ref': True,
            'toc_include_index': True,
            'toc_include_glossary': True,
            'toc_include_acronym': True,
            'toc_include_citation': True,
            'toc_include_target': True,
            'toc_include_substitution': True,
            'toc_include_footnote': True,
            'toc_include_citation': True,
            'toc_include_reference': True,
            'toc_include_hyperlink': True,
            'toc_include_anonymous': True,
            'toc_include_uri': True,
            'toc_include_email': True,
            'toc_include_tel': True,
            'toc_include_manpage': True,
            'toc_include_rfc': True,
            'toc_include_pep': True,
            'toc_include_rst': True,
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

        # Обработка callouts в стиле Notion
        if self.get_option('callouts'):
            html = self._process_callouts(html)

        # Обработка подсветки синтаксиса
        if self.get_option('syntax_highlight'):
            html = self.syntax_highlighter.process_content(html)

        return html

    def _process_callouts(self, html: str) -> str:
        """Преобразует блоки предупреждений в callouts."""
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

        return re.sub(
            r'<div class="admonition (\w+)">.*?<p class="first admonition-title">(.*?)</p>(.*?)</div>',
            admonition_to_callout,
            html,
            flags=re.DOTALL
        )

    def set_setting(self, key: str, value: Any) -> None:
        """Устанавливает настройку парсера RST."""
        self.settings[key] = value
        self.options[key] = value  # Для совместимости с базовым классом 