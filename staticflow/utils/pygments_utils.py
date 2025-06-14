"""Utilities for generating Pygments CSS styles."""
from pygments.formatters import HtmlFormatter
import logging

logger = logging.getLogger(__name__)

# Список доступных стилей для документации
AVAILABLE_STYLES = [
    "monokai", "default", "emacs", "vs", "xcode", "colorful", 
    "dracula", "github", "gruvbox-dark", "solarized-dark", "solarized-light",
    "nord", "tango", "zenburn"
]

def generate_pygments_css(style_name="monokai", custom_styles=None):
    """
    Generate Pygments CSS for syntax highlighting.
    
    Args:
        style_name: The Pygments style name to use (default: monokai)
        custom_styles: Additional CSS styles to append to the generated CSS
        
    Returns:
        str: Complete CSS for syntax highlighting
    """
    try:
        # Получаем базовые стили от Pygments для выбранной темы
        formatter = HtmlFormatter(style=style_name)
        pygments_css = formatter.get_style_defs('.highlight')
        
        # Добавляем минимальные необходимые стили для корректного отображения
        essential_css = """
/* Основные стили для корректного отображения */
.highlight {
    tab-size: 4 !important;
    -moz-tab-size: 4 !important;
    -o-tab-size: 4 !important;
    -webkit-tab-size: 4 !important;
    white-space: pre !important;
    letter-spacing: normal !important;
    word-spacing: normal !important;
    font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}

.highlight pre {
    padding: 1em;
    margin: 0;
    overflow-x: auto;
    background: transparent !important;
    white-space: pre !important;
}

.highlight .line {
    display: block;
    white-space: pre !important;  /* Сохраняем пробелы и табуляцию */
    position: relative;
    padding-left: 0; /* Уберем отступ */
}

/* ВАЖНО: CSS для корректного отображения пробелов */
.highlight .w {
    display: inline !important;
    white-space: pre !important;
    width: 0.25em !important; /* Фиксированная ширина для пробела */
    margin: 0 !important;
    padding: 0 !important;
    visibility: visible !important;
    opacity: 1 !important;
    font-size: inherit !important;
    line-height: inherit !important;
}

/* Фикс для пробелов между ключевыми словами и идентификаторами */
.highlight .k + .w, 
.highlight .kd + .w,
.highlight .kn + .w,
.highlight .kr + .w,
.highlight .kt + .w,
.highlight .ow + .w {
    visibility: visible !important;
    display: inline !important;
    width: auto !important;
    margin-right: 0.35em !important;
}

/* Специальные классы для отступов в начале строки */
.highlight .ws {
    white-space: pre !important;
    display: inline !important;
    visibility: visible !important;
    color: transparent !important;
    position: relative !important;
}

/* Добавляем отступы после ws */
.highlight .ws:after {
    content: ' ';
    display: inline;
    white-space: pre;
    margin-right: 0.5em;
}

/* Более надежное отображение пробелов */
.highlight .ws, .highlight .w {
    font-size: inherit !important;
    line-height: inherit !important;
}

/* Убираем слияние пробелов */
.highlight * {
    word-spacing: normal !important;
    letter-spacing: normal !important;
}

/* Усиленный фикс для пробелов */
.highlight .w:after {
    content: '' !important; /* Убираем дополнительный контент */
}

.highlight .w:before {
    content: '' !important;
}

/* Стили для кода с табуляцией */
.highlight.has-tabs {
    position: relative;
}

/* ======= Универсальные стили для всех языков ======= */

/* Фикс для отображения шаблонных строк JavaScript */
.highlight .sb, .highlight .s, .highlight .sa, .highlight .sc, 
.highlight .dl, .highlight .sd, .highlight .s2, .highlight .se, 
.highlight .sh, .highlight .si, .highlight .sx, .highlight .sr, 
.highlight .s1, .highlight .ss {
    white-space: pre !important;
}

/* Фикс для специальных символов во всех языках */
.highlight .nb, .highlight .nf, .highlight .nx, .highlight .nc {
    margin-left: 0.25em !important;
}

/* Фикс для отображения операторов во всех языках */
.highlight .o, .highlight .ow {
    margin: 0 0.25em !important;
}

/* Фикс для пунктуации */
.highlight .p {
    white-space: pre !important;
}

.code-block {
    position: relative;
    margin: 1em 0;
    border-radius: 4px;
    overflow: hidden;
    background: #272822;  /* Фон Monokai */
    color: #f8f8f2;       /* Цвет текста Monokai */
}

.language-tag {
    position: absolute;
    top: 0;
    right: 0;
    padding: 2px 8px;
    background: #333;
    color: #fff;
    font-size: 12px;
    border-radius: 0 0 0 4px;
    z-index: 10;
}

/* JavaScript специфичные фиксы */
.language-javascript .sb code.inline-code,
.javascript .sb code.inline-code,
.language-js .sb code.inline-code,
.js .sb code.inline-code {
    background: transparent !important;
    padding: 0 !important;
    font-family: inherit !important;
    font-size: inherit !important;
    display: inline !important;
}

/* Python специфичные фиксы */
.language-python .k + .n,
.python .k + .n {
    margin-left: 0.25em !important;
}

/* Ruby специфичные фиксы */
.language-ruby .n, .ruby .n {
    margin-left: 0.25em !important;
}

/* PHP специфичные фиксы */
.language-php .k + .n, .php .k + .n {
    margin-left: 0.25em !important;
}

/* C/C++ специфичные фиксы */
.language-c .kt + .n, .language-cpp .kt + .n, 
.c .kt + .n, .cpp .kt + .n {
    margin-left: 0.25em !important;
}

/* Java специфичные фиксы */
.language-java .kd + .n, .java .kd + .n {
    margin-left: 0.25em !important;
}

/* C# специфичные фиксы */
.language-csharp .k + .n, .csharp .k + .n {
    margin-left: 0.25em !important;
}

/* Go специфичные фиксы */
.language-go .k + .n, .go .k + .n {
    margin-left: 0.25em !important;
}

/* Rust специфичные фиксы */
.language-rust .k + .n, .rust .k + .n {
    margin-left: 0.25em !important;
}

/* TypeScript специфичные фиксы */
.language-typescript .k + .n, .typescript .k + .n,
.language-ts .k + .n, .ts .k + .n {
    margin-left: 0.25em !important;
}

/* Swift специфичные фиксы */
.language-swift .k + .n, .swift .k + .n {
    margin-left: 0.25em !important;
}

/* Kotlin специфичные фиксы */
.language-kotlin .k + .n, .kotlin .k + .n {
    margin-left: 0.25em !important;
}
"""
        
        # Объединяем стили
        css = f"{pygments_css}\n\n{essential_css}"
        
        # Добавляем пользовательские стили, если они предоставлены
        if custom_styles:
            css = f"{css}\n\n{custom_styles}"
        
        return css
        
    except Exception as e:
        logger.error(f"Error generating Pygments CSS: {e}")
        return "/* Error generating Pygments CSS */" 