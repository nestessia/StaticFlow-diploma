# StaticFlow API Documentation

## Core Components

### Engine

The main component responsible for site generation.

```python
from staticflow.core.engine import Engine
from staticflow.core.config import Config

# Initialize engine
engine = Engine(config)

# Build site
engine.build()
```

#### Methods

- `build()`: Build the entire site
- `process_file(path)`: Process a single file
- `render_template(template, context)`: Render a template with context

### Config

Configuration management for StaticFlow.

```python
from staticflow.core.config import Config
from pathlib import Path

# Load config from file
config = Config(Path('config.toml'))

# Get configuration values
site_name = config.get('site_name')
base_url = config.get('base_url')

# Set configuration values
config.set('site_name', 'My Site')
```

#### Configuration Options

- `site_name`: Site name
- `base_url`: Base URL for the site
- `description`: Site description
- `author`: Site author
- `language`: Site language code

### Page

Represents a content page.

```python
from staticflow.core.page import Page
from pathlib import Path

# Create page from file
page = Page(Path('content/post.md'))

# Access page properties
title = page.title
content = page.content
metadata = page.metadata
```

#### Properties

- `title`: Page title
- `content`: Page content
- `metadata`: Page metadata
- `template`: Template name
- `url`: Page URL

## Development Server

### DevServer

Development server with hot reload support.

```python
from staticflow.cli.server import DevServer

# Create server
server = DevServer(config, host='localhost', port=8000)

# Start server
server.start()
```

#### Features

- Hot reload
- Static file serving
- Live preview
- Debug information

## Admin Panel

### AdminPanel

Web-based admin interface.

```python
from staticflow.admin import AdminPanel

# Create admin panel
admin = AdminPanel(config, engine)

# Start admin panel
admin.start(host='localhost', port=8001)
```

### API Endpoints

#### Content Management

- `GET /content`: List content files
- `POST /api/content`: Create/update/delete content
  ```json
  {
    "action": "create",
    "path": "posts/new-post.md",
    "content": "# New Post\n\nContent here..."
  }
  ```

#### Settings Management

- `GET /settings`: Get site settings
- `POST /api/settings`: Update settings
  ```json
  {
    "site_name": "My Site",
    "base_url": "http://example.com"
  }
  ```

## Cache System

### Cache

Caching system for improved performance.

```python
from staticflow.core.cache import Cache
from pathlib import Path

# Initialize cache
cache = Cache(Path('.cache'))

# Basic operations
cache.set('key', 'value')
value = cache.get('key')
cache.delete('key')

# With namespace and expiration
from datetime import timedelta
cache.set('key', 'value', 
         namespace='pages',
         expires=timedelta(hours=1))

# Get cache statistics
stats = cache.get_stats()

# Clean up expired entries
cleaned = cache.cleanup()
```

#### Features

- Memory and file-based caching
- Namespace support
- Expiration support
- Cache statistics
- Automatic cleanup

## Plugin System

### Creating Plugins

```python
from staticflow.plugins.core.base import Plugin

class MyPlugin(Plugin):
    """Custom plugin example."""
    
    def __init__(self, config):
        super().__init__(config)
        
    def process_content(self, content):
        """Process content before rendering."""
        return content.replace('old', 'new')
        
    def process_page(self, page):
        """Process page after creation."""
        page.metadata['processed_by'] = self.name
        return page
```

### Using Plugins

```python
from staticflow.core.engine import Engine
from my_plugin import MyPlugin

# Create engine with plugin
engine = Engine(config)
engine.add_plugin(MyPlugin(config))

# Build site with plugins
engine.build()
```

## Command Line Interface

### Commands

- `staticflow create PATH`: Create new project
  ```bash
  staticflow create my-site
  ```

- `staticflow build`: Build site
  ```bash
  staticflow build --config config.toml
  ```

- `staticflow serve`: Start development server
  ```bash
  staticflow serve --host localhost --port 8000
  ```

### Options

- `--config, -c`: Path to config file
- `--host, -h`: Host for development server
- `--port, -p`: Port for development server

## Error Handling

### Common Errors

- `ConfigError`: Configuration-related errors
- `TemplateError`: Template processing errors
- `ContentError`: Content processing errors
- `BuildError`: Site building errors

### Error Handling Example

```python
from staticflow.core.exceptions import StaticFlowError

try:
    engine.build()
except StaticFlowError as e:
    print(f"Error building site: {e}")
```

## Best Practices

1. **Project Structure**
   ```
   my-site/
   ├── content/
   │   └── posts/
   ├── templates/
   │   └── base.html
   ├── static/
   │   └── css/
   ├── public/
   └── config.toml
   ```

2. **Configuration**
   - Use environment-specific configs
   - Keep sensitive data in environment variables
   - Document custom settings

3. **Content Organization**
   - Use consistent naming conventions
   - Organize content in subdirectories
   - Include proper metadata

4. **Performance**
   - Enable caching in production
   - Use incremental builds
   - Optimize static assets

5. **Development**
   - Use the development server
   - Enable debug mode during development
   - Test plugins thoroughly 