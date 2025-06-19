from typing import Any, Dict, List, Optional, Union
import markdown
from bs4 import BeautifulSoup
from .base import ContentParser
from .extensions.video import makeExtension as makeVideoExtension
from .extensions.audio import makeExtension as makeAudioExtension
from datetime import datetime
import frontmatter
import re


class MarkdownParser(ContentParser):
    """Парсер для Markdown контента."""

    def __init__(
        self,
        extensions: Optional[List[Union[str, Any]]] = None
    ) -> None:
        super().__init__()
        self.extensions: List[Union[str, Any]] = extensions or [
            'pymdownx.superfences',
            'codehilite',
            'fenced_code',
            'tables',
            'toc',
            'meta',
            'attr_list',
            'def_list',
            'footnotes',
            'md_in_html',
            makeVideoExtension(),
            makeAudioExtension(),
        ]
        self.extension_configs: Dict[str, Dict[str, Any]] = {
            'toc': {
                'toc_depth': 3
            },
            'codehilite': {
                'css_class': 'highlight',
                'linenums': False,
                'guess_lang': True,
                'use_pygments': True,
                'noclasses': False,
                'pygments_style': 'monokai'
            },
            'pymdownx.superfences': {
                'preserve_tabs': True,
                'css_class': 'highlight',
                'disable_indented_code_blocks': False
            },
            'fenced_code': {
                'lang_prefix': 'language-'
            }
        }

        # Создаем экземпляр Markdown с нужными настройками
        self._md: markdown.Markdown = markdown.Markdown(
            extensions=self.extensions,
            extension_configs=self.extension_configs,
            output_format='html5'
        )

    def parse(self, content: str) -> str:
        """Преобразует Markdown в HTML."""
        # Сохраняем блоки кода
        code_blocks = {}
        content = self._preserve_code_blocks(content, code_blocks)
        
        # Сохраняем отступы в HTML блоках
        content = self._preserve_html_indentation(content)
        
        # Конвертируем markdown в HTML
        html = self._md.convert(content)
        
        # Восстанавливаем блоки кода
        html = self._restore_code_blocks(html, code_blocks)
        
        # Форматируем HTML с сохранением отступов
        html = self._format_html(html)
        
        return html

    def _preserve_code_blocks(self, content: str, code_blocks: dict) -> str:
        """Сохраняет блоки кода, заменяя их на маркеры."""
        def replace_fenced_block(match):
            nonlocal code_blocks
            block_id = f"CODE_BLOCK_{len(code_blocks)}"
            
            # Определяем язык из заголовка блока кода
            lang = match.group(1).strip() if match.group(1) else ''
            code = match.group(2)
            
            # Форматируем код в HTML
            if lang:
                code_html = (
                    f'<pre><code class="language-{lang}">{code}</code></pre>'
                )
            else:
                code_html = f'<pre><code>{code}</code></pre>'
            
            code_blocks[block_id] = code_html
            return block_id

        def replace_inline_code(match):
            nonlocal code_blocks
            block_id = f"CODE_BLOCK_{len(code_blocks)}"
            code = match.group(1)
            code_html = f'<code class="language-text">{code}</code>'
            code_blocks[block_id] = code_html
            return block_id
        
        # Сначала обрабатываем блоки кода с тройными кавычками
        content = re.sub(
            r'```([^\n]*)\n(.*?)\n```',
            replace_fenced_block,
            content,
            flags=re.DOTALL
        )
        
        # Затем обрабатываем inline код
        content = re.sub(
            r'`([^`]+)`',
            replace_inline_code,
            content
        )
        
        return content

    def _restore_code_blocks(self, html: str, code_blocks: dict) -> str:
        """Восстанавливает блоки кода из маркеров."""
        for block_id, code_block in code_blocks.items():
            html = html.replace(block_id, code_block)
        return html

    def _preserve_html_indentation(self, content: str) -> str:
        """Сохраняет отступы в HTML блоках."""
        lines = []
        current_indent = 0
        in_code_block = False
        code_indent = 0
        
        for line in content.split('\n'):
            stripped = line.lstrip()
            if not stripped:
                lines.append(line)
                continue
            
            # Проверяем, не находимся ли мы в блоке кода
            if 'CODE_BLOCK_' in line:
                in_code_block = True
                code_indent = len(line) - len(stripped)
                lines.append(line)
                continue
            
            # Если мы в блоке кода, сохраняем текущий отступ
            if in_code_block:
                if code_indent > 0:
                    spaces = ' ' * code_indent
                    lines.append(spaces + stripped)
                else:
                    lines.append(line)
                if '</code>' in line:
                    in_code_block = False
                continue
            
            # Если это HTML тег
            if stripped.startswith('<') and not stripped.startswith('<!'):
                if stripped.startswith('</'):  # Закрывающий тег
                    current_indent = max(0, current_indent - 4)
                spaces = ' ' * current_indent
                lines.append(spaces + stripped)
                if not stripped.startswith('</'):  # Открывающий тег
                    current_indent += 4
            else:
                spaces = ' ' * current_indent
                lines.append(spaces + stripped)
        
        return '\n'.join(lines)

    def _format_html(self, html: str) -> str:
        """Форматирует HTML с сохранением отступов."""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Не форматируем содержимое pre и code
        for pre in soup.find_all('pre'):
            pre.string = pre.decode_contents()
        
        # Настраиваем форматирование
        formatted_html = str(soup.prettify(formatter='minimal'))
        
        # Заменяем пробелы в начале строк на табуляцию
        lines = []
        for line in formatted_html.split('\n'):
            stripped = line.lstrip()
            if stripped:
                indent = len(line) - len(stripped)
                # Используем 4 пробела для отступа
                tabs = ' ' * indent
                lines.append(tabs + stripped)
            else:
                lines.append(line)
        
        return '\n'.join(lines)

    def add_extension(
        self,
        extension: str,
        config: Optional[Dict[str, Any]] = None
    ) -> None:
        """Добавляет расширение Markdown."""
        if extension not in self.extensions:
            self.extensions.append(extension)
            if config:
                self.extension_configs[extension] = config
            self._md = markdown.Markdown(
                extensions=self.extensions,
                extension_configs=self.extension_configs
            )

    def validate(self, content: str) -> bool:
        """Валидирует Markdown контент."""
        if content is None:
            return False
        if not isinstance(content, str):
            return False
        if not content.strip():
            return False
        return True

    def get_metadata(self, content: str) -> Dict[str, Any]:
        """Получает метаданные из Markdown контента."""
        try:
            post = frontmatter.loads(content)
            metadata = dict(post.metadata)
            
            # Преобразуем строковую дату в объект datetime
            if 'date' in metadata and isinstance(metadata['date'], str):
                try:
                    metadata['date'] = datetime.strptime(
                        metadata['date'], 
                        '%Y-%m-%d'
                    ).date()
                except ValueError:
                    pass
                    
            return metadata
        except Exception:
            return {}
