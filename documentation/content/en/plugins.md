---
title: Plugins
date: 2025-05-20
author: nestessia
tags: [plugins, extensions, development]
format: markdown
template: en_page.html
language: en
---

# 🔌 Plugins

This section covers the StaticFlow plugin system and how to create your own plugins.

## 🤔 What is a plugin?

A plugin in StaticFlow is an extension that adds new functionality or modifies existing functionality. Plugins can:

- ✨ Add new content formats
- 🎨 Extend template functionality
- 🖥️ Add new CLI commands
- 🔗 Integrate external services
- ⚡ Optimize the build process
- 🖼️ Process media files
- 🌐 Support multilingual content

## 🏗️ Plugin System Architecture

### Core Components

#### **Plugin (Base Class)**
```python
class Plugin(ABC):
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.enabled: bool = True
        self._hooks: Dict[HookType, List[str]] = {}
```

#### **PluginMetadata (Metadata)**
```python
@dataclass
class PluginMetadata:
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None
    requires_config: bool = False
    priority: int = 100
```

#### **HookType (Hook Types)**
```python
class HookType(Enum):
    PRE_BUILD = auto()          # Before site build
    POST_BUILD = auto()         # After site build
    PRE_PAGE = auto()          # Before page processing
    POST_PAGE = auto()         # After page processing
    PRE_TEMPLATE = auto()      # Before template rendering
    POST_TEMPLATE = auto()     # After template rendering
    PRE_ASSET = auto()         # Before asset processing
    POST_ASSET = auto()        # After asset processing
```

## 📦 Installing plugins

### Via pip

```bash
pip install staticflow-plugin-name
```

### In configuration

```toml
# config.toml
[PLUGINS]
enabled = [
    "syntax_highlight",
    "math",
    "media",
    "cdn",
    "seo"
]

[PLUGIN_SYNTAX_HIGHLIGHT]
style = "monokai"
linenums = false
css_class = "highlight"

[PLUGIN_MEDIA]
output_dir = "media"
sizes = { "thumbnail" = { width = 200, height = 200 } }
formats = ["webp", "original"]
```

## 🛠️ Creating a plugin

### 1. Plugin structure

```
my-plugin/
├── staticflow_my_plugin/
│   ├── __init__.py
│   ├── plugin.py
│   └── utils.py
├── tests/
│   └── test_plugin.py
├── setup.py
├── README.md
└── LICENSE
```

### 2. Main plugin code

```python
# staticflow_my_plugin/plugin.py
from staticflow.plugins.core.base import Plugin, PluginMetadata
from typing import Dict, Any

class MyPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="my-plugin",
            version="1.0.0",
            description="Description of my plugin",
            author="Your Name",
            requires_config=False,
            priority=100
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin."""
        super().initialize(config)
        # Your initialization logic
    
    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before site build."""
        # Prepare for build
        return context
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook after page processing."""
        # Modify page content
        content = context.get('content', '')
        # Your content processing
        context['content'] = content
        return context
    
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Hook before asset processing."""
        # Process static files
        return context
    
    def cleanup(self) -> None:
        """Cleanup plugin resources."""
        # Cleanup resources
        pass
```

### 3. Plugin registration

```python
# staticflow_my_plugin/__init__.py
from .plugin import MyPlugin

def register(engine):
    plugin = MyPlugin()
    engine.add_plugin(plugin)
    return plugin
```

### 4. Setup.py configuration

```python
# setup.py
from setuptools import setup, find_packages

setup(
    name="staticflow-my-plugin",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "staticflow>=1.0.0",
    ],
    entry_points={
        "staticflow.plugins": [
            "my-plugin = staticflow_my_plugin:register",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="Description of my plugin",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/your-username/staticflow-my-plugin",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
    ],
)
```

## 🎯 Plugin types

### 📝 Content plugins

```python
class ContentPlugin(Plugin):
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process page content."""
        content = context.get('content', '')
        # Modify content
        context['content'] = processed_content
        return context
```

### 🎨 Template plugins

```python
class TemplatePlugin(Plugin):
    def on_post_template(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Process after template rendering."""
        # Modify context or template
        return context
```

### 🖥️ CLI plugins

```python
class CLIPlugin(Plugin):
    def register_commands(self, cli):
        @cli.command()
        def my_command():
            """Command description"""
            # Command code
            pass
```

### ⚡ Build plugins

```python
class BuildPlugin(Plugin):
    def on_pre_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for build."""
        # Prepare resources
        return context
    
    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Cleanup after build."""
        # Cleanup temporary files
        return context
```

## 🔗 Plugin hooks

### 🔄 Lifecycle hooks

- `on_pre_build` - before site build
- `on_post_build` - after site build
- `initialize` - plugin initialization
- `cleanup` - resource cleanup

### 📄 Page hooks

- `on_pre_page` - before page processing
- `on_post_page` - after page processing
- `process_content` - content processing

### 🎨 Template hooks

- `on_pre_template` - before template rendering
- `on_post_template` - after template rendering

### 📁 Asset hooks

- `on_pre_asset` - before asset processing
- `on_post_asset` - after asset processing

## ⚙️ Plugin configuration

### Default settings

```python
class MyPlugin(Plugin):
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        default_config = {
            'option1': 'default1',
            'option2': 'default2',
        }
        
        # Merge with user configuration
        self.config = {**default_config, **(config or {})}
        super().initialize()
```

### Settings validation

```python
def validate_config(self) -> bool:
    """Validate plugin configuration."""
    required = ['option1', 'option2']
    for option in required:
        if option not in self.config:
            raise ValueError(f"Missing required setting: {option}")
    return True
```

## 🧪 Testing plugins

### Unit tests

```python
# tests/test_plugin.py
import pytest
from staticflow_my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin()
    assert plugin.metadata.name == "my-plugin"
    assert plugin.metadata.version == "1.0.0"

def test_plugin_config():
    config = {'option1': 'value1'}
    plugin = MyPlugin()
    plugin.initialize(config)
    assert plugin.config['option1'] == 'value1'

def test_plugin_hooks():
    plugin = MyPlugin()
    context = {'content': 'test content'}
    
    # Test hook
    result = plugin.on_post_page(context)
    assert 'content' in result
```

### Integration tests

```python
def test_plugin_integration():
    from staticflow.core.engine import Engine
    from staticflow.core.config import Config
    
    # Create test engine
    config = Config("test_config.toml")
    engine = Engine(config)
    
    # Add plugin
    plugin = MyPlugin()
    engine.add_plugin(plugin)
    
    # Test functionality
    assert engine.get_plugin("my-plugin") == plugin
```

## 📦 Built-in plugins

### 🔍 SEO Plugin
```python
# Automatic Open Graph tags
# Twitter Card tags
# Schema.org markup
# Headers and images optimization
```

### 🗺️ Sitemap Plugin
```python
# Generate sitemap.xml
# Automatic updates
# Priority support
```

### 📡 RSS Plugin
```python
# Generate RSS feeds
# Category support
# Automatic updates
```

### 🖼️ Media Plugin
```python
# Image processing
# WebP generation
# Srcset creation
# Video optimization
```

### 🌐 CDN Plugin
```python
# CDN integration
# Automatic file upload
# Cache purging
```

### 💎 Syntax Highlight Plugin
```python
# Code syntax highlighting
# Multiple language support
# Customizable themes
```

### ➗ Math Plugin
```python
# Mathematical formula rendering
# LaTeX support
# Automatic rendering
```

### 📊 Mermaid Plugin
```python
# Diagram creation
# Various types support
# Interactive diagrams
```

## 🚀 Publishing plugins

### Preparation

1. 📝 Create README.md
2. 📄 Add license
3. 📚 Write documentation
4. 🧪 Create tests
5. 🔧 Setup CI/CD

### Publishing to PyPI

```bash
# Build package
python setup.py sdist bdist_wheel

# Upload to PyPI
twine upload dist/*
```

### Updates

1. 🔢 Increment version
2. 📚 Update documentation
3. 🔄 Add migrations
4. 🚀 Publish new version

## 💡 Best practices

### 🛠️ Development

1. 📏 Follow PEP 8
2. 🧪 Write tests
3. 📝 Document code
4. 🏷️ Use type hints
5. 🔍 Handle errors

### ⚡ Performance

1. 🚀 Optimize operations
2. 💾 Use caching
3. 📦 Minimize dependencies
4. 💻 Monitor memory usage
5. 🔄 Use async operations

### 🔒 Security

1. ✅ Validate input data
2. 🔐 Use secure settings
3. ⚠️ Handle errors
4. 🔄 Monitor updates
5. 🛡️ Check dependencies

### 🔗 Compatibility

1. 🐍 Support Python versions
2. 🧪 Test on different versions
3. 📋 Document dependencies
4. 👀 Monitor API changes
5. 🔄 Ensure backward compatibility

## 🎯 Usage examples

### Simple plugin for adding meta tags

```python
class MetaTagsPlugin(Plugin):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="meta-tags",
            version="1.0.0",
            description="Adds meta tags to pages",
            author="Your Name"
        )
    
    def on_post_page(self, context: Dict[str, Any]) -> Dict[str, Any]:
        content = context.get('content', '')
        
        # Add meta tags
        meta_tags = f"""
        <meta name="generator" content="StaticFlow">
        <meta name="author" content="{context.get('author', 'Unknown')}">
        <meta name="date" content="{context.get('date', '')}">
        """
        
        # Insert into head
        if '<head>' in content:
            content = content.replace('<head>', f'<head>{meta_tags}')
        
        context['content'] = content
        return context
```

### Plugin for image processing

```python
class ImageProcessorPlugin(Plugin):
    def on_pre_asset(self, context: Dict[str, Any]) -> Dict[str, Any]:
        file_path = context.get('file_path')
        
        if self._is_image(file_path):
            # Process image
            processed_path = self._process_image(file_path)
            context['file_path'] = processed_path
        
        return context
    
    def _is_image(self, path: str) -> bool:
        return path.lower().endswith(('.png', '.jpg', '.jpeg', '.gif'))
    
    def _process_image(self, path: str) -> str:
        # Image processing logic
        return path
```