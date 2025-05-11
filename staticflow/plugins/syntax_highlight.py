import re
import logging
import html
from typing import Dict, Any, Optional
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer, guess_lexer
from .base import Plugin

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SyntaxHighlight")


class SyntaxHighlightPlugin(Plugin):
    """Plugin for syntax highlighting code blocks in content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        linenums = self.config.get('linenums', False)
        
        logger.info("Initializing SyntaxHighlightPlugin")
        
        # Получаем стиль из глобального конфига сайта, если он есть
        style = self.config.get('style', 'monokai')
        if (hasattr(self, 'engine') and self.engine 
                and hasattr(self.engine, 'config')):
            syntax_config = self.engine.config.get("syntax_highlight", {})
            style = syntax_config.get("style", style)
        
        logger.info(f"Using style: {style}")
        
        # Create formatter with explicit settings for tabulation
        self.formatter = HtmlFormatter(
            style=style,
            cssclass=self.config.get('css_class', 'highlight'),
            linenos=linenums,
            noclasses=False,
            tabsize=4,
            # Critical settings for preserving tabs and newlines
            prestyles="white-space: pre !important; tab-size: 4 !important;",
            nobackground=True,
            tabreplace='',  # Preserve tabs instead of converting to spaces
        )
        
    def _detect_language_from_code(self, code):
        """Detect language from code content."""
        # Detect Python by keywords
        if (re.search(r'\bdef\s+\w+\s*\(', code) or 
                re.search(r'\bclass\s+\w+\s*\(', code) or 
                re.search(r'\bimport\s+\w+', code) or
                re.search(r'\bprint\s*\(', code)):
            logger.info("Detected Python from code content")
            return "python"
        
        # Try to guess language automatically with Pygments
        try:
            lexer = guess_lexer(code)
            lang = lexer.aliases[0]
            logger.info(f"Pygments detected language: {lang}")
            return lang
        except Exception:
            logger.info("Failed to detect language, using text")
            return "text"
    
    def _decode_entities(self, content):
        """Decode HTML entities to normal characters."""
        return html.unescape(content)
    
    def _process_code_with_linebreaks(self, code, lexer):
        """Process code with Pygments while preserving line breaks and tabs.
        
        This method preserves the structure of the original code by adding
        line breaks and proper spacing.
        """
        # Запоминаем, есть ли табы
        has_tabs = '\t' in code
        
        # Получаем HTML-разметку от Pygments с базовой подсветкой
        formatted_html = highlight(code, lexer, self.formatter)
        
        # Прямые исправления специфических проблем с пробелами в HTML
        # Python: исправляем пробелы после ключевых слов
        replacements = [
            # Python ключевые слова
            ('<span class="k">def</span>', '<span class="k">def</span><span class="w"> </span>'),
            ('<span class="k">if</span>', '<span class="k">if</span><span class="w"> </span>'),
            ('<span class="k">for</span>', '<span class="k">for</span><span class="w"> </span>'),
            ('<span class="k">while</span>', '<span class="k">while</span><span class="w"> </span>'),
            ('<span class="k">class</span>', '<span class="k">class</span><span class="w"> </span>'),
            ('<span class="k">import</span>', '<span class="k">import</span><span class="w"> </span>'),
            ('<span class="k">from</span>', '<span class="k">from</span><span class="w"> </span>'),
            ('<span class="k">in</span>', '<span class="k">in</span><span class="w"> </span>'),
            ('<span class="k">as</span>', '<span class="k">as</span><span class="w"> </span>'),
            ('<span class="k">return</span>', '<span class="k">return</span><span class="w"> </span>'),
            ('<span class="k">with</span>', '<span class="k">with</span><span class="w"> </span>'),
            ('<span class="k">try</span>', '<span class="k">try</span><span class="w"> </span>'),
            ('<span class="k">except</span>', '<span class="k">except</span><span class="w"> </span>'),
            ('<span class="k">finally</span>', '<span class="k">finally</span><span class="w"> </span>'),
            ('<span class="k">else</span>', '<span class="k">else</span><span class="w"> </span>'),
            ('<span class="k">elif</span>', '<span class="k">elif</span><span class="w"> </span>'),
            
            # JavaScript ключевые слова
            ('<span class="kd">function</span>', '<span class="kd">function</span><span class="w"> </span>'),
            ('<span class="kd">let</span>', '<span class="kd">let</span><span class="w"> </span>'),
            ('<span class="kd">const</span>', '<span class="kd">const</span><span class="w"> </span>'),
            ('<span class="kd">var</span>', '<span class="kd">var</span><span class="w"> </span>'),
            ('<span class="k">if</span>', '<span class="k">if</span><span class="w"> </span>'),
            ('<span class="k">for</span>', '<span class="k">for</span><span class="w"> </span>'),
            ('<span class="k">while</span>', '<span class="k">while</span><span class="w"> </span>'),
            ('<span class="k">return</span>', '<span class="k">return</span><span class="w"> </span>'),
            ('<span class="k">switch</span>', '<span class="k">switch</span><span class="w"> </span>'),
            ('<span class="k">case</span>', '<span class="k">case</span><span class="w"> </span>'),
            
            # Операторы
            ('<span class="o">=</span>', '<span class="o">=</span><span class="w"> </span>'),
            ('<span class="o">+</span>', '<span class="o">+</span><span class="w"> </span>'),
            ('<span class="o">-</span>', '<span class="o">-</span><span class="w"> </span>'),
            ('<span class="o">*</span>', '<span class="o">*</span><span class="w"> </span>'),
            ('<span class="o">/</span>', '<span class="o">/</span><span class="w"> </span>'),
            ('<span class="o">%</span>', '<span class="o">%</span><span class="w"> </span>'),
            ('<span class="o">==</span>', '<span class="o">==</span><span class="w"> </span>'),
            ('<span class="o">!=</span>', '<span class="o">!=</span><span class="w"> </span>'),
            ('<span class="o">&lt;</span>', '<span class="o">&lt;</span><span class="w"> </span>'),
            ('<span class="o">&gt;</span>', '<span class="o">&gt;</span><span class="w"> </span>'),
            ('<span class="o">&lt;=</span>', '<span class="o">&lt;=</span><span class="w"> </span>'),
            ('<span class="o">&gt;=</span>', '<span class="o">&gt;=</span><span class="w"> </span>'),
        ]
        
        # Применяем все замены
        for old, new in replacements:
            formatted_html = formatted_html.replace(old, new)

        # Извлекаем содержимое между тегами <pre>
        pattern = r'<pre[^>]*>(.*?)</pre>'
        pre_match = re.search(pattern, formatted_html, re.DOTALL)
        if not pre_match:
            return formatted_html
            
        pre_content = pre_match.group(1)
        
        # Разбиваем по строкам и добавляем line spans
        lines = pre_content.split('\n')
        processed_lines = []
        
        # Получаем оригинальные строки для сравнения
        orig_lines = code.split('\n')
        
        for i, (line, orig_line) in enumerate(zip(lines, orig_lines)):
            # Если строка пустая, добавляем пустую строку
            if not orig_line.strip():
                processed_lines.append(
                    f'<span class="line" id="L{i+1}">&nbsp;</span>'
                )
                continue
            
            # Точное копирование отступов из оригинального кода
            # Находим отступы в оригинальной строке
            indent_match = re.match(r'^(\s+)', orig_line)
            if indent_match:
                orig_indent = indent_match.group(1)
                
                # Сохраняем фактические символы табуляции и пробелов
                indent_html = '<span class="ws">'
                
                # Преобразуем каждый символ отступа в соответствующее представление
                for char in orig_indent:
                    if char == ' ':
                        indent_html += '&#160;'  # неразрывный пробел в HTML
                    elif char == '\t':
                        # Для таба добавляем фактический символ табуляции
                        # или 4 неразрывных пробела для совместимости
                        indent_html += '&#160;&#160;&#160;&#160;'
                
                indent_html += '</span>'
                
                # Заменяем отступы в текущей строке HTML
                line = re.sub(r'^\s*', indent_html, line)
            
            # Оборачиваем в span с классом line
            processed_lines.append(
                f'<span class="line" id="L{i+1}">{line}</span>'
            )
        
        # Собираем все строки в один блок
        processed_content = '\n'.join(processed_lines)
        
        # Заменяем содержимое на обработанное
        formatted_html = formatted_html.replace(
            pre_match.group(1), processed_content
        )
        
        # Включаем пробелы в стили
        if 'white-space: pre' not in formatted_html:
            style = 'white-space: pre !important; tab-size: 4 !important;'
            formatted_html = formatted_html.replace(
                '<pre>', f'<pre style="{style}">'
            )
        
        # Добавляем класс has-tabs, если есть табы
        if has_tabs:
            formatted_html = formatted_html.replace(
                'class="highlight"', 
                'class="highlight has-tabs"'
            )
            
        return formatted_html
    
    def _get_token_class(self, token_type):
        """Получить CSS-класс для типа токена Pygments."""
        # Преобразуем токен в CSS-класс
        ttype = token_type
        cls = ''
        while ttype:
            if ttype in self.formatter.ttype2class:
                cls = self.formatter.ttype2class[ttype]
                break
            ttype = ttype.parent
        if not cls:
            cls = 'text'  # Значение по умолчанию
        return cls
    
    def process_content(self, content: str) -> str:
        """Process content and highlight code blocks."""
        if not content or len(content) < 10:
            return content
        
        logger.info("Starting syntax highlighting processing")
        
        # Function for highlighting code with tab/newline preservation
        def highlight_block(code, lang):
            try:
                # Decode HTML entities properly
                code = self._decode_entities(code)
                
                try:
                    # Try to get lexer by language
                    lexer = get_lexer_by_name(lang)
                except ValueError:
                    # Try to detect language automatically
                    detected_lang = self._detect_language_from_code(code)
                    lang = detected_lang
                    try:
                        lexer = get_lexer_by_name(lang)
                    except ValueError:
                        lexer = TextLexer()
                
                # Process code with Pygments, preserving tabs and newlines
                html_code = self._process_code_with_linebreaks(code, lexer)
                
                # Create code block with language tag on separate lines
                # for better readability in the output
                result = (
                    '<div class="code-block language-{0}">\n'
                    '    <div class="language-tag">{0}</div>\n'
                    '    {1}\n'
                    '</div>'
                ).format(lang, html_code)
                
                return result
            except Exception as e:
                logger.error(f"Error highlighting code: {e}")
                # Fallback to simple HTML with line breaks
                escaped = html.escape(code)
                return f'<pre><code>{escaped}</code></pre>'
        
        # Process markdown code blocks: ```lang ...code... ```
        def process_md_block(match):
            lang = match.group(1).strip() if match.group(1) else 'text'
            code = match.group(2)
            
            # Особая обработка Mermaid диаграмм
            if lang.lower() == 'mermaid':
                # Преобразуем блок mermaid в div.mermaid
                return f'<div class="mermaid">{code}</div>'
                
            logger.info(f"Processing markdown code block: {lang}")
            return highlight_block(code, lang)
        
        # Find all markdown code blocks
        md_pattern = re.compile(
            r'```\s*([a-zA-Z0-9_+-]+)?\s*\n((?:(?!```).|\n)+?)\s*```',
            re.MULTILINE
        )
        content = md_pattern.sub(process_md_block, content)
        
        # Process HTML code blocks: <pre><code>...</code></pre>
        def process_html_block(match):
            full_match = match.group(0)
            code = match.group(1)
            
            # Look for language in class attribute
            lang_match = re.search(
                r'class=["\'](.*?language-(\w+))["\']', full_match
            )
            
            if lang_match:
                lang = lang_match.group(2)
                # Особая обработка Mermaid диаграмм
                if lang.lower() == 'mermaid':
                    return f'<div class="mermaid">{code}</div>'
            else:
                # Detect language by content
                lang = self._detect_language_from_code(code)
            
            logger.info(f"Processing HTML code block: {lang}")
            return highlight_block(code, lang)
        
        # Find HTML code blocks
        html_pattern = re.compile(
            r'<pre>\s*<code.*?>(.*?)</code>\s*</pre>',
            re.DOTALL
        )
        content = html_pattern.sub(process_html_block, content)
        
        # Process inline code: `code`
        content = re.sub(
            r'`([^`\n]+)`',
            lambda m: f'<code class="inline-code">'
                      f'{html.escape(m.group(1))}</code>',
            content
        )
        
        # Process RST code blocks: <pre class="code ...">...</pre>
        def process_rst_block(match):
            class_attr = match.group(1)
            code = match.group(2)
            # Если уже есть pygments-разметка, не трогаем
            if '<span class=' in code:
                return match.group(0)
            # Извлекаем язык из классов
            lang_match = re.search(
                r'code\s+([a-zA-Z0-9_+-]+)', class_attr
            )
            lang = lang_match.group(1) if lang_match else 'text'
            return highlight_block(code, lang)

        rst_pattern = re.compile(
            r'<pre class="code ([^"]+)">(.*?)</pre>',
            re.DOTALL
        )
        content = rst_pattern.sub(process_rst_block, content)
        
        return content