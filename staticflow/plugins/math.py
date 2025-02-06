from typing import Dict, Any, Optional
import re
import markdown
from .base import Plugin


class MathPlugin(Plugin):
    """Plugin for rendering mathematical formulas using KaTeX."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.katex_css = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">'
        self.katex_js = '''
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"
                onload="renderMathInElement(document.body);"></script>
        '''

    def process_content(self, content: str) -> str:
        """Process content and render math formulas."""
        # Process inline math: $formula$
        content = re.sub(
            r'\$(.+?)\$',
            lambda m: f'<span class="math inline">{m.group(1)}</span>',
            content
        )

        # Process display math: $$formula$$
        content = re.sub(
            r'\$\$(.*?)\$\$',
            lambda m: f'<div class="math display">{m.group(1)}</div>',
            content,
            flags=re.DOTALL
        )

        return content

    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return f"{self.katex_css}\n{self.katex_js}" 