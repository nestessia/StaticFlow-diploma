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
                    '<div class="mermaid">'
                    f'{diagram_content}</div>'
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
        # Подключаем самую базовую версию Mermaid
        mermaid_script = (
            '<script src="https://cdn.jsdelivr.net/npm/'
            'mermaid@8.14.0/dist/mermaid.min.js"></script>'
        )
        init_script = """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
            // Базовая инициализация с минимальными настройками
            if (typeof mermaid !== 'undefined') {
                // Конфигурация с минимумом настроек
                mermaid.initialize({
                    startOnLoad: true,
                    theme: 'default',
                    securityLevel: 'loose'
                });
            }
        });
        </script>
        <style>
        /* Простые стили для диаграмм */
        .mermaid {
            margin: 1.5rem 0;
            text-align: center;
            background: #f8f9fa;
            padding: 1rem;
            border-radius: 0.5rem;
            border: 1px solid #e5e7eb;
        }
        </style>
        """
        return f'{mermaid_script}\n{init_script}'
