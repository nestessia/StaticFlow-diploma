from typing import Dict, Any, Optional
import re
from .base import Plugin


class MathPlugin(Plugin):
    """Plugin for rendering mathematical formulas using KaTeX."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.katex_css = '<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.css">'
        self.katex_js = '''
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/katex.min.js"></script>
            <script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.9/dist/contrib/auto-render.min.js"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {
                    renderMathInElement(document.body, {
                        delimiters: [
                            {left: "\\\\[", right: "\\\\]", display: true},
                            {left: "\\\\(", right: "\\\\)", display: false}
                        ],
                        throwOnError: false
                    });
                });
            </script>
        '''

    def process_content(self, content: str) -> str:
        """Process content and render math formulas."""
        # Process inline math: $formula$
        content = re.sub(
            r'\$([^$]+?)\$',
            r'\\(\1\\)',
            content
        )

        # Process display math: $$formula$$
        content = re.sub(
            r'\$\$(.*?)\$\$',
            r'\\[\1\\]',
            content,
            flags=re.DOTALL
        )

        return content

    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.katex_css + self.katex_js 