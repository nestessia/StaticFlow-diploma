import pytest
from staticflow.plugins.syntax_highlight import SyntaxHighlightPlugin
from staticflow.plugins.math import MathPlugin
from staticflow.plugins.diagrams import MermaidPlugin
from staticflow.plugins.notion_blocks import NotionBlocksPlugin


def test_syntax_highlight_plugin():
    """Test syntax highlighting plugin."""
    plugin = SyntaxHighlightPlugin()
    
    # Test Python code highlighting
    content = '''
Here is some code:
```python
def hello():
    print("Hello, World!")
```
'''
    processed = plugin.process_content(content)
    assert '<div class="highlight">' in processed
    assert 'def hello()' in processed
    assert 'print("Hello, World!")' in processed
    
    # Test unknown language
    content = '''```unknown
some code
```'''
    processed = plugin.process_content(content)
    assert '<div class="highlight">' in processed
    assert 'some code' in processed
    
    # Test CSS generation
    css = plugin.get_css()
    assert '.highlight' in css


def test_math_plugin():
    """Test math plugin."""
    plugin = MathPlugin()
    
    # Test inline math
    content = 'Here is an inline formula: $E = mc^2$'
    processed = plugin.process_content(content)
    assert '<span class="math inline">E = mc^2</span>' in processed
    
    # Test display math
    content = '''Here is a display formula:
$$
\\int_0^\\infty e^{-x} dx = 1
$$'''
    processed = plugin.process_content(content)
    assert '<div class="math display">' in processed
    assert '\\int_0^\\infty e^{-x} dx = 1' in processed
    
    # Test head content
    head = plugin.get_head_content()
    assert 'katex.min.css' in head
    assert 'katex.min.js' in head
    assert 'auto-render.min.js' in head


def test_mermaid_plugin():
    """Test Mermaid diagrams plugin."""
    plugin = MermaidPlugin()
    
    # Test diagram rendering
    content = '''Here is a diagram:
```mermaid
graph TD
    A[Start] --> B[Process]
    B --> C[End]
```'''
    processed = plugin.process_content(content)
    assert '<div class="mermaid">' in processed
    assert 'graph TD' in processed
    assert 'A[Start] --> B[Process]' in processed
    assert 'B --> C[End]' in processed
    
    # Test head content
    head = plugin.get_head_content()
    assert 'mermaid.min.js' in head
    assert 'mermaid.initialize' in head 


def test_notion_blocks_plugin():
    """Test Notion-style blocks plugin."""
    plugin = NotionBlocksPlugin()
    
    # Test callout block
    content = '''
Some text
:::info This is important
Important information here
:::
More text
'''
    processed = plugin.process_content(content)
    assert '<div class="callout info">' in processed
    assert '<div class="callout-icon">ℹ️</div>' in processed
    assert 'Important information here' in processed
    
    # Test toggle block
    content = '''
>>> Click to expand
Hidden content here
<<<
'''
    processed = plugin.process_content(content)
    assert '<div class="toggle">' in processed
    assert '<div class="toggle-header">▶ Click to expand</div>' in processed
    assert 'Hidden content here' in processed
    
    # Test todo list
    content = '''
- [ ] Unchecked task
- [x] Checked task
'''
    processed = plugin.process_content(content)
    assert '<div class="todo-item">' in processed
    assert '<input type="checkbox" class="todo-checkbox" >' in processed
    assert '<input type="checkbox" class="todo-checkbox" checked>' in processed
    
    # Test table
    content = '''
||Header 1|Header 2
Row 1 Col 1|Row 1 Col 2
Row 2 Col 1|Row 2 Col 2||
'''
    processed = plugin.process_content(content)
    assert '<table class="table-view">' in processed
    assert '<th>Header 1</th>' in processed
    assert '<td>Row 1 Col 1</td>' in processed
    
    # Test head content
    head = plugin.get_head_content()
    assert '.callout {' in head
    assert '.toggle {' in head
    assert '.todo-item {' in head
    assert '.table-view {' in head 