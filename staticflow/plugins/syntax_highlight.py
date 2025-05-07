from typing import Dict, Any, Optional
import re
import logging
import html
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
        
        # Create formatter with explicit settings for tabulation
        self.formatter = HtmlFormatter(
            style=self.config.get('style', 'monokai'),
            cssclass=self.config.get('css_class', 'highlight'),
            linenos=linenums,
            wrapcode=True,  
            noclasses=False,
            tabsize=4,
            # Специальное сохранение всех пробелов и табуляции
            prestyles="white-space: pre !important; tab-size: 4 !important;"
        )
        
    def _detect_language_from_code(self, code):
        """Detect language from code content."""
        # Детекция Python по ключевым словам
        if (re.search(r'\bdef\s+\w+\s*\(', code) or 
                re.search(r'\bclass\s+\w+\s*\(', code) or 
                re.search(r'\bimport\s+\w+', code) or
                re.search(r'\bprint\s*\(', code)):
            logger.info("Автоопределение Python по содержимому кода")
            return "python"
        
        # Пытаемся угадать язык автоматически через Pygments
        try:
            lexer = guess_lexer(code)
            lang = lexer.aliases[0]
            logger.info(f"Pygments определил язык: {lang}")
            return lang
        except Exception:
            logger.info("Не удалось определить язык, используем text")
            return "text"
    
    def _decode_entities(self, content):
        """Раскодировать HTML-сущности в обычные символы."""
        # Заменяем HTML-сущности на обычные символы
        return (content
            .replace("&quot;", '"')
            .replace("&apos;", "'")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace("&amp;", "&")
        )
    
    def process_content(self, content: str) -> str:
        """Process content and highlight code blocks."""
        if not content or len(content) < 10:
            return content
        
        logger.info("Начало обработки подсветки синтаксиса")
        
        # Основная функция для подсветки кода
        def highlight_code(code, lang):
            try:
                # Декодируем HTML-сущности для нормальной подсветки кода
                code = self._decode_entities(code)
                
                # Сохраняем все пробелы и табуляции, заменяя табы на 4 пробела
                # только для отображения, не для нарушения структуры
                has_tabs = '\t' in code
                if has_tabs:
                    logger.info("Найдена табуляция в коде")
                
                try:
                    # Пытаемся получить лексер для указанного языка
                    lexer = get_lexer_by_name(lang)
                    logger.info(f"Используем лексер для {lang}")
                except ValueError:
                    # Пробуем определить язык по содержимому
                    detected_lang = self._detect_language_from_code(code)
                    logger.info(f"Используем {detected_lang} вместо {lang}")
                    try:
                        lexer = get_lexer_by_name(detected_lang)
                    except ValueError:
                        lexer = TextLexer()
                
                # Выполняем подсветку кода
                highlighted = highlight(code, lexer, self.formatter)
                
                # Добавляем специальную CSS-разметку для сохранения табуляции
                if has_tabs:
                    # Добавляем класс для родительского элемента
                    highlighted = highlighted.replace(
                        '<div class="highlight">',
                        '<div class="highlight has-tabs">'
                    )
                
                # Создаем блок с указанием языка
                return f'''<div class="code-block language-{lang}">
                    <div class="language-tag">{lang}</div>
                    {highlighted}
                </div>'''
            except Exception as e:
                logger.error(f"Ошибка подсветки кода: {e}")
                # В случае ошибки возвращаем простой блок кода
                escaped_code = html.escape(code)
                return f'<pre><code>{escaped_code}</code></pre>'
        
        # Функция для обработки HTML блоков <pre><code>
        def process_html_code_block(match):
            full_match = match.group(0)
            pre_content = match.group(1)
            
            # Декодируем HTML-сущности
            pre_content = self._decode_entities(pre_content)
            
            # Ищем атрибуты для определения языка
            lang_match = re.search(r'class=["\'](.*?language-(\w+))["\']', full_match)
            
            if lang_match:
                lang = lang_match.group(2)
                logger.info(f"Найден блок кода HTML с языком: {lang}")
            else:
                # Определяем язык по содержимому
                lang = self._detect_language_from_code(pre_content)
                logger.info(f"Автоопределение языка: {lang}")
            
            return highlight_code(pre_content, lang)
            
        # Обрабатываем уже преобразованные блоки кода (от markdown)
        html_pattern = re.compile(
            r'<pre>\s*<code.*?>(.*?)</code>\s*</pre>', 
            re.DOTALL
        )
        content = html_pattern.sub(process_html_code_block, content)
        
        # Обрабатываем сырые markdown блоки кода
        def process_raw_code_block(match):
            lang = match.group(1).strip() if match.group(1) else ''
            code = match.group(2)
            
            logger.info(f"Найден сырой markdown блок с языком: {lang}")
            
            # Если язык не указан, определяем по содержимому
            if not lang:
                lang = self._detect_language_from_code(code)
            
            return highlight_code(code, lang)
        
        # Ищем markdown-блоки с кодом
        raw_pattern = re.compile(
            r'```\s*([a-zA-Z0-9_+-]+)?\s*\n((?:(?!```).|\n)+?)\s*```',
            re.MULTILINE
        )
        content = raw_pattern.sub(process_raw_code_block, content)
        
        # Обрабатываем инлайн-код
        content = re.sub(
            r'`([^`\n]+)`', 
            lambda m: f'<code class="inline-code">{m.group(1)}</code>', 
            content
        )
        
        return content
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        # Базовые стили Pygments
        base_styles = self.formatter.get_style_defs()
        
        # Добавляем кастомные стили
        additional_styles = """
        /* Custom monospace font */
        @font-face {
            font-family: 'CodeFont';
            src: local('Consolas'), local('Liberation Mono'), 
                 local('Menlo'), local('Monaco'), local('Courier New'), 
                 monospace;
            font-display: swap;
        }

        /* Code block styling */
        .code-block {
            margin: 1.5rem 0;
            position: relative;
            border-radius: 0.5rem;
            overflow: hidden;
        }
        
        /* Language tag */
        .language-tag {
            position: absolute;
            top: 0;
            right: 0;
            padding: 3px 10px;
            font-size: 0.75rem;
            font-family: sans-serif;
            color: white;
            background: #444;
            border-radius: 0 0.3rem 0 0.3rem;
            z-index: 5;
        }
        
        /* Language-specific colors */
        .language-python .language-tag { background: #306998; }
        .language-js .language-tag, 
        .language-javascript .language-tag { 
            background: #f0db4f; 
            color: black; 
        }
        .language-html .language-tag { background: #e34c26; }
        .language-css .language-tag { background: #264de4; }
        
        /* Highlight block */
        .highlight {
            background: #272822 !important;
            color: #f8f8f2 !important;
            padding: 1.25rem !important;
            margin: 0 !important;
            overflow-x: auto !important;
            tab-size: 4 !important;
            -moz-tab-size: 4 !important;
        }
        
        /* Force proper handling of tabs and spaces */
        .highlight.has-tabs .hll,
        .highlight.has-tabs pre,
        .highlight.has-tabs code,
        .highlight.has-tabs span {
            tab-size: 4 !important;
            -moz-tab-size: 4 !important;
            white-space: pre !important;
        }
        
        /* All code elements */
        .highlight pre, 
        .highlight code, 
        .highlight span {
            font-family: 'CodeFont', monospace !important;
            white-space: pre !important;
            tab-size: 4 !important;
            -moz-tab-size: 4 !important;
        }
        
        /* Pre element styling */
        .highlight pre {
            margin: 0 !important;
            padding: 0 !important;
            background: transparent !important;
            border: none !important;
        }
        
        /* Code element styling */
        .highlight code {
            display: block !important;
            font-size: 14px !important;
            background: transparent !important;
        }
        
        /* Inline code */
        code.inline-code {
            background-color: #f5f5f5;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-family: 'CodeFont', monospace;
            font-size: 90%;
        }
        
        /* Ensure token colors are visible */
        .highlight .c { color: #75715e !important; } /* Comment */
        .highlight .k { color: #66d9ef !important; } /* Keyword */
        .highlight .n { color: #f8f8f2 !important; } /* Name */
        .highlight .o { color: #f92672 !important; } /* Operator */
        .highlight .p { color: #f8f8f2 !important; } /* Punctuation */
        .highlight .s { color: #e6db74 !important; } /* String */
        .highlight .na { color: #a6e22e !important; } /* Name.Attribute */
        .highlight .nf { color: #a6e22e !important; } /* Name.Function */
        .highlight .s1, .highlight .s2 { color: #e6db74 !important; } /* Strings */
        .highlight .kw { color: #66d9ef !important; } /* Keywords */
        
        /* Tab character implementation */
        .tab, .highlight .tab {
            display: inline-block;
            width: 4em;
            height: 1em;
        }
        """
        
        return f'<style>{base_styles}{additional_styles}</style>'