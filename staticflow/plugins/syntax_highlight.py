from typing import Dict, Any, Optional
import re
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import get_lexer_by_name, TextLexer
from .base import Plugin


class SyntaxHighlightPlugin(Plugin):
    """Plugin for syntax highlighting code blocks in content."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.formatter = HtmlFormatter(
            style=self.config.get('style', 'monokai'),
            cssclass=self.config.get('css_class', 'highlight'),
            linenos=self.config.get('line_numbers', False)
        )
        
    def process_content(self, content: str) -> str:
        """Process content and highlight code blocks."""
        def replace_code_block(match: re.Match) -> str:
            lang = match.group(1) or 'text'
            code = match.group(2)
            
            try:
                lexer = get_lexer_by_name(lang)
            except ValueError:
                lexer = TextLexer()
                
            return highlight(code, lexer, self.formatter)
            
        # Find and replace code blocks
        pattern = r'```(\w+)?\n(.*?)\n```'
        return re.sub(pattern, replace_code_block, content, flags=re.DOTALL)
    
    def get_css(self) -> str:
        """Get the CSS for syntax highlighting."""
        return self.formatter.get_style_defs() 