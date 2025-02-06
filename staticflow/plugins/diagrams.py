from typing import Dict, Any, Optional
from markdown import Extension
from markdown.preprocessors import Preprocessor
from .base import Plugin


class MermaidPreprocessor(Preprocessor):
    """Preprocessor for handling Mermaid diagrams in Markdown."""
    
    def run(self, lines):
        new_lines = []
        is_mermaid = False
        mermaid_lines = []
        
        for line in lines:
            # Проверяем начало блока Mermaid
            if line.strip().startswith('```') and 'mermaid' in line.strip():
                is_mermaid = True
                continue
            # Проверяем конец блока
            elif is_mermaid and line.strip() == '```':
                is_mermaid = False
                # Собираем диаграмму и оборачиваем в div
                diagram = '\n'.join(mermaid_lines).strip()
                new_lines.append(f'<div class="mermaid">{diagram}</div>')
                mermaid_lines = []
                continue
            
            if is_mermaid:
                mermaid_lines.append(line)
            else:
                new_lines.append(line)
        
        return new_lines


class MermaidExtension(Extension):
    """Markdown extension for Mermaid diagrams."""
    
    def extendMarkdown(self, md):
        # Регистрируем препроцессор с высоким приоритетом
        # Он должен выполниться до обработки блоков кода
        md.preprocessors.register(
            MermaidPreprocessor(md),
            'mermaid',
            200  # Приоритет выше, чем у fenced_code (30)
        )


class MermaidPlugin(Plugin):
    """Plugin for rendering Mermaid diagrams."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.mermaid_js = '''
            <script src="https://cdn.jsdelivr.net/npm/mermaid@8.14.0/dist/mermaid.min.js"></script>
            <script>
                document.addEventListener('DOMContentLoaded', function() {
                    mermaid.initialize({
                        startOnLoad: true,
                        theme: 'default',
                        securityLevel: 'loose'
                    });
                });
            </script>
        '''
    
    def initialize(self) -> None:
        """Initialize the plugin and register Markdown extension."""
        if hasattr(self.engine, 'markdown'):
            self.engine.markdown.registerExtension(MermaidExtension())
    
    def process_content(self, content: str) -> str:
        """Process content and render Mermaid diagrams."""
        return content  # Обработка уже выполнена через Markdown расширение
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.mermaid_js