from typing import Dict, Any, Optional
import re
from .base import Plugin


class MermaidPlugin(Plugin):
    """Plugin for rendering Mermaid diagrams."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mermaid_js = '''
            <script src="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js"></script>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    mermaid.initialize({
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose',
                        flowchart: {
                            htmlLabels: true,
                            curve: 'linear'
                        }
                    });
                });
            </script>
        '''
        
    def process_content(self, content: str) -> str:
        """Process content and render Mermaid diagrams."""
        def replace_diagram(match: re.Match) -> str:
            diagram = match.group(1).strip()
            # Remove any extra whitespace and ensure proper line breaks
            lines = [line.strip() for line in diagram.split('\n') if line.strip()]
            diagram = '\n'.join(lines)
            return f'<pre class="mermaid">{diagram}</pre>'
            
        # Find and replace Mermaid diagrams
        pattern = r'```mermaid\s*(.*?)\s*```'
        content = re.sub(pattern, replace_diagram, content, flags=re.DOTALL)
        return content
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.mermaid_js 