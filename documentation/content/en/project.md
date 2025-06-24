---
title: Project
date: 2025-05-20
author: nestessia
tags: [project, structure, concepts]
format: markdown
template: page.html
language: en
---

# StaticFlow Project

This section covers the main concepts and structure of a StaticFlow project.

## Project structure

A typical StaticFlow project has the following structure:

```
project/
├── content/          # Source content files
├── templates/        # HTML templates
├── static/          # Static files (CSS, JS, images)
├── output/          # Generated site
├── media/           # Media files
└── config.toml      # Project configuration
```

## Main concepts

### Content

Content in StaticFlow is stored as Markdown files in the `content/` directory. Each file can contain metadata in front matter format:

```yaml
---
title: Page Title
date: 2024-03-20
author: author
tags: [tag1, tag2]
format: markdown
template: page.html
---
```

### Templates

Templates define the appearance of pages. They use Jinja2 as the template engine and can include:
- Base templates
- Partial templates
- Macros
- Template inheritance

### Static files

The `static/` directory contains all static files that are copied to `output/` without changes:
- CSS styles
- JavaScript files
- Images
- Other media files

### Configuration

The `config.toml` file defines the main project settings:
- Site name
- Base URL
- Languages
- URL patterns
- Plugins
- Other settings

## Content organization

### Categories

StaticFlow supports hierarchical content organization through categories:
- Categories can be nested

- Maximum nesting depth is configurable

- Each category can have its own page

### Tags

Tags allow grouping content by topics:
- Case insensitive

- Limit on number of tags

- Automatic tag page generation

### Authors

The author system allows:
- Linking content to authors

- Creating author profiles

- Generating author pages

## Plugins

StaticFlow has a plugin system that allows:
- Extending functionality
- Adding new content formats
- Integrating external services
- Customizing the build process 