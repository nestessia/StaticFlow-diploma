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
        # Основные стили от Pygments для выбранной темы
        formatter = HtmlFormatter(style=style_name)
        pygments_css = formatter.get_style_defs('.highlight')
        return pygments_css

    except Exception as e:
        logger.error(f"Error generating Pygments CSS: {e}")
        # Fallback to empty CSS
        return "/* Error generating Pygments CSS */" 