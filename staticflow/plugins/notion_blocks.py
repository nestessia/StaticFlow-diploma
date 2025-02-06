from typing import Dict, Any, Optional
import re
from .base import Plugin


class NotionBlocksPlugin(Plugin):
    """Plugin for Notion-style content blocks."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self.notion_css = '''
            <style>
            .callout {
                padding: 1.25rem;
                margin: 1.5rem 0;
                border-radius: 0.5rem;
                display: flex;
                align-items: flex-start;
                gap: 1rem;
                background: var(--bg-color, #ffffff);
                border: 1px solid var(--border-color, #e5e7eb);
            }
            
            .callout-icon {
                font-size: 1.5rem;
                line-height: 1;
                flex-shrink: 0;
            }
            
            .callout-content {
                flex: 1;
                min-width: 0;
            }
            
            .callout.info {
                --bg-color: #f1f5f9;
                --border-color: #3b82f6;
            }
            
            .callout.warning {
                --bg-color: #fef3c7;
                --border-color: #f59e0b;
            }
            
            .callout.error {
                --bg-color: #fee2e2;
                --border-color: #ef4444;
            }
            
            .toggle {
                margin: 1rem 0;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                overflow: hidden;
            }
            
            .toggle-header {
                cursor: pointer;
                padding: 1rem;
                background: #f8fafc;
                display: flex;
                align-items: center;
                gap: 0.75rem;
                font-weight: 500;
            }
            
            .toggle-content {
                padding: 1rem;
                border-top: 1px solid #e5e7eb;
                display: none;
            }
            
            .toggle.open .toggle-content {
                display: block;
            }
            
            .todo-list {
                list-style: none;
                padding: 0;
                margin: 1rem 0;
            }
            
            .todo-item {
                display: flex;
                align-items: center;
                gap: 0.75rem;
                padding: 0.5rem;
                border-radius: 0.25rem;
                transition: background-color 0.2s;
            }
            
            .todo-item:hover {
                background: #f8fafc;
            }
            
            .todo-checkbox {
                width: 1.25rem;
                height: 1.25rem;
                border: 2px solid #e5e7eb;
                border-radius: 0.25rem;
                cursor: pointer;
            }
            
            .todo-item.completed {
                color: #9ca3af;
                text-decoration: line-through;
            }
            
            .table-view {
                width: 100%;
                border-collapse: collapse;
                margin: 1.5rem 0;
                border: 1px solid #e5e7eb;
                border-radius: 0.5rem;
                overflow: hidden;
            }
            
            .table-view th,
            .table-view td {
                padding: 0.75rem 1rem;
                border: 1px solid #e5e7eb;
            }
            
            .table-view th {
                background: #f8fafc;
                font-weight: 600;
                text-align: left;
            }
            
            .table-view tr:hover {
                background: #f8fafc;
            }
            </style>
            <script>
            document.addEventListener('DOMContentLoaded', function() {
                // Toggle blocks
                document.querySelectorAll('.toggle-header').forEach(header => {
                    header.addEventListener('click', () => {
                        const toggle = header.parentElement;
                        const isOpen = toggle.classList.contains('open');
                        toggle.classList.toggle('open');
                        header.querySelector('.toggle-icon').textContent = 
                            isOpen ? '▶' : '▼';
                    });
                });
                
                // Todo checkboxes
                document.querySelectorAll('.todo-checkbox').forEach(checkbox => {
                    checkbox.addEventListener('change', () => {
                        checkbox.parentElement.classList.toggle('completed');
                    });
                });
            });
            </script>
        '''
        
    def process_content(self, content: str) -> str:
        """Process content and convert Notion-style blocks."""
        # Process callouts
        content = re.sub(
            r':::(\w+)\s+(.*?):::',
            lambda m: self._create_callout(m.group(1), m.group(2)),
            content,
            flags=re.DOTALL
        )
        
        # Process toggles
        content = re.sub(
            r'>>>\s+(.*?)\n(.*?)<<<',
            lambda m: self._create_toggle(m.group(1), m.group(2)),
            content,
            flags=re.DOTALL
        )
        
        # Process todo lists
        content = re.sub(
            r'- \[([ x])\] (.*?)(?:\n|$)',
            lambda m: self._create_todo_item(m.group(1), m.group(2)),
            content
        )
        
        # Process tables
        content = re.sub(
            r'\|\|(.*?)\|\|',
            lambda m: self._create_table(m.group(1)),
            content,
            flags=re.DOTALL
        )
        
        return content
    
    def _create_callout(self, type_: str, content: str) -> str:
        """Create a callout block."""
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌'
        }
        icon = icons.get(type_, 'ℹ️')
        return f'''
            <div class="callout {type_}">
                <div class="callout-icon">{icon}</div>
                <div class="callout-content">{content.strip()}</div>
            </div>
        '''
    
    def _create_toggle(self, summary: str, content: str) -> str:
        """Create a toggle block."""
        return f'''
            <div class="toggle">
                <div class="toggle-header">▶ {summary.strip()}</div>
                <div class="toggle-content">{content.strip()}</div>
            </div>
        '''
    
    def _create_todo_item(self, checked: str, content: str) -> str:
        """Create a todo list item."""
        checked_attr = 'checked' if checked == 'x' else ''
        return f'''
            <div class="todo-item">
                <input type="checkbox" class="todo-checkbox" {checked_attr}>
                <span>{content.strip()}</span>
            </div>
        '''
    
    def _create_table(self, content: str) -> str:
        """Create a table view."""
        rows = content.strip().split('\n')
        html_rows = []
        
        for i, row in enumerate(rows):
            cells = row.strip('|').split('|')
            cell_tag = 'th' if i == 0 else 'td'
            html_cells = [f'<{cell_tag}>{cell.strip()}</{cell_tag}>' for cell in cells]
            html_rows.append(f'<tr>{"".join(html_cells)}</tr>')
            
        return f'''
            <table class="table-view">
                {"".join(html_rows)}
            </table>
        '''
    
    def get_head_content(self) -> str:
        """Get content to be inserted in the head section."""
        return self.notion_css 