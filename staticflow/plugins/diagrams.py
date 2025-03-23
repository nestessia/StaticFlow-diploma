"""Mermaid diagrams plugin for StaticFlow."""

from markdown.preprocessors import Preprocessor
from markdown.extensions import Extension
from .base import Plugin


class MermaidPreprocessor(Preprocessor):
    """Preprocessor for Mermaid diagrams."""
    
    def run(self, lines):
        new_lines = []
        is_mermaid = False
        diagram = []
        
        for line in lines:
            if line.strip() == '```mermaid':
                is_mermaid = True
                continue
            elif line.strip() == '```' and is_mermaid:
                is_mermaid = False
                diagram_content = '\n'.join(diagram)
                new_lines.append(
                    '<pre class="mermaid" data-processed="false">'
                    f'{diagram_content}</pre>'
                )
                diagram = []
                continue
                
            if is_mermaid:
                diagram.append(line)
            else:
                new_lines.append(line)
                
        return new_lines


class MermaidExtension(Extension):
    """Markdown extension for Mermaid diagrams."""
    
    def extendMarkdown(self, md):
        """Add MermaidPreprocessor to the Markdown instance."""
        md.preprocessors.register(
            MermaidPreprocessor(md),
            'mermaid',
            175
        )


class MermaidPlugin(Plugin):
    """Plugin for rendering Mermaid diagrams."""
    
    def __init__(self):
        super().__init__()
        self.name = 'mermaid'
        self.description = 'Renders Mermaid diagrams in Markdown files'
        
    def init(self, engine):
        """Initialize the plugin with the engine instance."""
        super().init(engine)
        self.engine = engine
        self.engine.md.registerExtension(MermaidExtension())
        
    def process_content(self, content: str) -> str:
        """Process content and render Mermaid diagrams."""
        # Обработка уже выполнена через Markdown расширение
        return content
        
    def get_head_content(self) -> str:
        """Return content to be added to the head section."""
        mermaid_script = (
            '<script src="https://cdn.jsdelivr.net/npm/'
            'mermaid@10.2.3/dist/mermaid.min.js"></script>'
        )
        init_script = """
        <script>
            mermaid.initialize({
                startOnLoad: true,
                theme: 'default'
            });
            mermaid.run();
        </script>
        """
        return f'{mermaid_script}\n{init_script}'