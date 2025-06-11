from typing import Dict, Any, Optional
from .base import Plugin


class MathPlugin(Plugin):
    """Plugin for rendering mathematical formulas using KaTeX."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        katex_url = 'https://cdn.jsdelivr.net/npm/katex@0.16.9/dist'
        self.katex_css = (
            f'<link rel="stylesheet" href="{katex_url}/katex.min.css">'
        )
        self.katex_js = f'''
            <script defer src="{katex_url}/katex.min.js"></script>
            <script defer src="{katex_url}/contrib/auto-render.min.js"></script>
            <script>
                document.addEventListener("DOMContentLoaded", function() {{
                    renderMathInElement(document.body, {{
                        delimiters: [
                            {{left: "$$", right: "$$", display: true}},
                            {{left: "$", right: "$", display: false}}
                        ],
                        throwOnError: false
                    }});
                }});
            </script>
        '''

    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.katex_css + self.katex_js
