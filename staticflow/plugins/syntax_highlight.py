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
        
        This method preserves the structure of the original code.
        """
        # Получаем полную HTML разметку от Pygments
        formatted_html = highlight(code, lexer, self.formatter)
        
        # Для сохранения переносов строк, добавляем line spans
        # Извлекаем содержимое между тегами <pre>
        match = re.search(r'<pre[^>]*>(.*?)</pre>', formatted_html, re.DOTALL)
        if match:
            # Получаем содержимое между тегами <pre>
            pre_content = match.group(1)
            
            # Разбиваем на строки и добавляем class="line"
            lines = pre_content.split('\n')
            processed_lines = []
            
            for i, line in enumerate(lines):
                if not line.strip():
                    # Добавляем пустую строку с неразрывным пробелом
                    processed_lines.append('<span class="line">&nbsp;</span>')
                else:
                    # Добавляем номер строки как id для возможности ссылок
                    processed_lines.append(
                        f'<span class="line" id="L{i+1}">{line}</span>'
                    )
            
            # Собираем обратно и заменяем в исходном HTML
            processed_content = '\n'.join(processed_lines)
            formatted_html = formatted_html.replace(
                match.group(1), processed_content
            )
        
        # Если в коде есть табуляция, добавляем специальный класс
        if '\t' in code:
            formatted_html = formatted_html.replace(
                'class="highlight"', 'class="highlight has-tabs"'
            )
            
        return formatted_html
    
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
                
                # Create code block with language tag
                return (
                    f'<div class="code-block language-{lang}">\n'
                    f'<div class="language-tag">{lang}</div>\n'
                    f'{html_code}\n'
                    f'</div>'
                )
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