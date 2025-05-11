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
    width: auto !important;
    margin: 0 !important;
    padding: 0 !important;
    visibility: visible !important;
    opacity: 1 !important;
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
    content: ' ';
    white-space: pre;
}

.highlight .w:before {
    content: '';
}

/* Стили для кода с табуляцией */
.highlight.has-tabs {
    position: relative;
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

/* Фикс для шаблонных строк JavaScript */
.language-javascript .sb code.inline-code,
.javascript .sb code.inline-code {
    background: transparent !important;
    padding: 0 !important;
    font-family: inherit !important;
    font-size: inherit !important;
    display: inline !important;
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