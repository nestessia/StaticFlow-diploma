from typing import Dict, Any, Optional
import re
from .base import Plugin


class MermaidPlugin(Plugin):
    """Plugin for rendering Mermaid diagrams."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mermaid_js = '''
            <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
            <script>
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default'
                });
            </script>
        '''
        
    def process_content(self, content: str) -> str:
        """Process content and render Mermaid diagrams."""
        def replace_diagram(match: re.Match) -> str:
            diagram = match.group(1)
            return f'<div class="mermaid">\n{diagram}\n</div>'
            
        # Find and replace Mermaid diagrams
        pattern = r'```mermaid\n(.*?)\n```'
        return re.sub(pattern, replace_diagram, content, flags=re.DOTALL)
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.mermaid_js 