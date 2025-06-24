---
title: Plugins
date: 2025-05-20
author: nestessia
tags: [plugins, extensions, development]
format: markdown
template: en_page.html
language: en
---

# Plugins

This section covers the StaticFlow plugin system and how to create your own plugins.

## What is a plugin?

A plugin in StaticFlow is an extension that adds new functionality or modifies existing functionality. Plugins can:

- Add new content formats
- Extend template functionality
- Add new CLI commands
- Integrate external services
- Optimize the build process

## Installing plugins

### Via pip

```bash
pip install staticflow-plugin-name
```

### In configuration

```toml
# config.toml
[PLUGINS]
enabled = [
    "plugin-name",
    "another-plugin"
]

[PLUGIN_PLUGIN_NAME]
setting1 = "value1"
setting2 = "value2"
```

## Creating a plugin

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
from staticflow.plugins import Plugin

class MyPlugin(Plugin):
    name = "my-plugin"
    version = "1.0.0"
    description = "Description of my plugin"

    def __init__(self, app):
        super().__init__(app)
        self.settings = app.config.get('PLUGIN_MY_PLUGIN', {})

    def on_build_start(self):
        # Code executed before build
        pass

    def on_build_end(self):
        # Code executed after build
        pass

    def on_page_render(self, page, template):
        # Modify page before rendering
        return page, template
```

### 3. Plugin registration

```python
# staticflow_my_plugin/__init__.py
from .plugin import MyPlugin

def register(app):
    return MyPlugin(app)
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

## Plugin types

### Content plugins

```python
class ContentPlugin(Plugin):
    def on_content_load(self, content):
        # Modify content
        return content

    def on_content_save(self, content):
        # Process before saving
        return content
```

### Template plugins

```python
class TemplatePlugin(Plugin):
    def on_template_render(self, template, context):
        # Modify template or context
        return template, context

    def register_filters(self, env):
        # Register custom filters
        env.filters['my_filter'] = my_filter_function
```

### CLI plugins

```python
class CLIPlugin(Plugin):
    def register_commands(self, cli):
        @cli.command()
        def my_command():
            """Command description"""
            # Command code
            pass
```

### Build plugins

```python
class BuildPlugin(Plugin):
    def on_build_start(self):
        # Prepare for build
        pass

    def on_build_end(self):
        # Cleanup after build
        pass

    def on_asset_process(self, asset):
        # Process assets
        return asset
```

## Plugin hooks

### Lifecycle hooks

- `on_init` - plugin initialization
- `on_build_start` - build start
- `on_build_end` - build end
- `on_clean` - cleanup

### Content hooks

- `on_content_load` - content loading
- `on_content_save` - content saving
- `on_page_render` - page rendering
- `on_post_render` - post rendering

### Template hooks

- `on_template_render` - template rendering
- `on_template_compile` - template compilation
- `on_context_update` - context update

### Asset hooks

- `on_asset_process` - asset processing
- `on_asset_save` - asset saving
- `on_asset_clean` - asset cleanup

## Plugin configuration

### Default settings

```python
class MyPlugin(Plugin):
    default_settings = {
        'option1': 'default1',
        'option2': 'default2',
    }

    def __init__(self, app):
        super().__init__(app)
        self.settings = {
            **self.default_settings,
            **app.config.get('PLUGIN_MY_PLUGIN', {})
        }
```

### Settings validation

```python
def validate_settings(self, settings):
    required = ['option1', 'option2']
    for option in required:
        if option not in settings:
            raise ValueError(f"Missing required setting: {option}")
```

## Testing plugins

### Unit tests

```python
# tests/test_plugin.py
import pytest
from staticflow_my_plugin import MyPlugin

def test_plugin_initialization():
    plugin = MyPlugin(mock_app)
    assert plugin.name == "my-plugin"
    assert plugin.version == "1.0.0"

def test_plugin_settings():
    plugin = MyPlugin(mock_app)
    assert plugin.settings['option1'] == 'default1'
```

### Integration tests

```python
def test_plugin_integration():
    app = create_test_app()
    plugin = MyPlugin(app)
    
    # Test functionality
    result = plugin.process_content("test content")
    assert result == "processed test content"
```

## Publishing plugins

### Preparation

1. Create README.md
2. Add license
3. Write documentation
4. Create tests

### Publishing to PyPI

```bash
python setup.py sdist bdist_wheel
twine upload dist/*
```

### Updates

1. Increment version
2. Update documentation
3. Add migrations
4. Publish new version

## Best practices

### Development

1. Follow PEP 8
2. Write tests
3. Document code
4. Use type hints

### Performance

1. Optimize operations
2. Use caching
3. Minimize dependencies
4. Monitor memory usage

### Security

1. Validate input data
2. Use secure settings
3. Handle errors
4. Monitor updates

### Compatibility

1. Support Python versions
2. Test on different versions
3. Document dependencies
4. Monitor API changes 