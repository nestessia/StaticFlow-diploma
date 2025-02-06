# StaticFlow User Guide

## Introduction

StaticFlow is a modern static site generator that combines simplicity with powerful features. This guide will help you get started and make the most of StaticFlow's capabilities.

## Installation

Install StaticFlow using pip:

```bash
pip install staticflow
```

## Quick Start

1. Create a new project:
   ```bash
   staticflow create my-site
   cd my-site
   ```

2. Start the development server:
   ```bash
   staticflow serve
   ```

3. Open your browser at `http://localhost:8000`

## Project Structure

A typical StaticFlow project has the following structure:

```
my-site/
├── content/          # Content files (Markdown, HTML)
│   ├── posts/        # Blog posts
│   └── pages/        # Static pages
├── templates/        # Template files
│   ├── base.html     # Base template
│   └── post.html     # Post template
├── static/           # Static files
│   ├── css/          # Stylesheets
│   ├── js/           # JavaScript files
│   └── images/       # Images
├── public/           # Generated site
└── config.toml       # Configuration file
```

## Content Creation

### Writing Content

StaticFlow supports both Markdown and HTML content files. Content files should include front matter metadata:

```markdown
---
title: My First Post
date: 2024-02-06
tags: [blog, tutorial]
template: post.html
---

# My First Post

This is my first blog post using StaticFlow.
```

### Content Organization

- Use descriptive filenames
- Organize content in subdirectories
- Include relevant metadata
- Choose appropriate templates

## Templates

### Template Syntax

StaticFlow uses Jinja2 for templates:

```html
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }} - {{ site.name }}</title>
</head>
<body>
    <header>
        <h1>{{ site.name }}</h1>
        <nav>
            {% for item in site.menu %}
            <a href="{{ item.url }}">{{ item.title }}</a>
            {% endfor %}
        </nav>
    </header>
    
    <main>
        {{ page.content }}
    </main>
    
    <footer>
        <p>&copy; {{ site.author }}</p>
    </footer>
</body>
</html>
```

### Available Variables

- `site`: Site-wide configuration
- `page`: Current page data
- `content`: Rendered page content

## Configuration

### Basic Configuration

Edit `config.toml`:

```toml
# Site Information
site_name = "My Site"
base_url = "http://example.com"
description = "My personal website"
author = "John Doe"
language = "en"

# Build Settings
content_dir = "content"
output_dir = "public"
static_dir = "static"

# Template Settings
template_dir = "templates"
default_template = "page.html"
```

### Environment-Specific Configuration

Create environment-specific config files:

- `config.development.toml`
- `config.production.toml`

## Admin Panel

### Accessing Admin Panel

1. Start the admin panel:
   ```bash
   staticflow serve
   ```

2. Open `http://localhost:8001/admin`

### Content Management

- Create, edit, and delete content
- Preview changes in real-time
- Manage media files
- Configure site settings

## Development Server

### Features

- Hot reload
- Live preview
- Error reporting
- Performance monitoring

### Options

```bash
staticflow serve --host localhost --port 8000 --config config.toml
```

## Building for Production

1. Update production configuration:
   ```toml
   # config.production.toml
   base_url = "https://mysite.com"
   ```

2. Build the site:
   ```bash
   staticflow build --config config.production.toml
   ```

3. Deploy the `public` directory

## Advanced Features

### Custom Plugins

Create a plugin:

```python
from staticflow.plugins.core.base import Plugin

class SyntaxHighlightPlugin(Plugin):
    def process_content(self, content):
        # Add syntax highlighting
        return highlighted_content
```

Register the plugin:

```python
engine.add_plugin(SyntaxHighlightPlugin(config))
```

### Caching

Enable caching for better performance:

```toml
# config.toml
[cache]
enabled = true
directory = ".cache"
ttl = 3600  # seconds
```

### Custom Templates

Create custom template filters:

```python
from staticflow.templates import register_filter

@register_filter
def truncate(text, length=100):
    return text[:length] + '...'
```

## Performance Optimization

1. **Enable Caching**
   - Use memory cache for development
   - Enable file cache for production
   - Set appropriate TTL values

2. **Optimize Assets**
   - Minify CSS and JavaScript
   - Optimize images
   - Use appropriate formats

3. **Incremental Builds**
   - Only rebuild changed files
   - Use content hashing
   - Enable parallel processing

## Troubleshooting

### Common Issues

1. **Build Errors**
   - Check template syntax
   - Verify front matter format
   - Check file permissions

2. **Server Issues**
   - Verify port availability
   - Check network settings
   - Review error logs

3. **Plugin Problems**
   - Check plugin compatibility
   - Review plugin documentation
   - Enable debug logging

### Debug Mode

Enable debug mode:

```bash
staticflow serve --debug
```

## Best Practices

1. **Content Management**
   - Use consistent naming
   - Include proper metadata
   - Organize content logically

2. **Development**
   - Use version control
   - Follow coding standards
   - Write tests

3. **Deployment**
   - Use CI/CD pipelines
   - Automate builds
   - Monitor performance

## Security

1. **Admin Panel**
   - Use strong passwords
   - Enable HTTPS
   - Restrict access

2. **Configuration**
   - Use environment variables
   - Secure sensitive data
   - Regular updates

## Getting Help

- Documentation: `docs/`
- Issues: GitHub Issues
- Community: Discord Server
- Email: support@staticflow.dev 