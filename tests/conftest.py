import pytest
from pathlib import Path
import shutil
import tempfile
from staticflow.core.config import Config
from staticflow.core.engine import Engine


@pytest.fixture
def temp_site_dir():
    """Create a temporary directory for site testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        
        # Create site structure
        (temp_path / "content").mkdir()
        (temp_path / "templates").mkdir()
        (temp_path / "static").mkdir()
        (temp_path / "public").mkdir()
        
        yield temp_path


@pytest.fixture
def sample_config(temp_site_dir):
    """Create a sample configuration."""
    config_data = {
        "site_name": "Test Site",
        "base_url": "http://localhost:8000",
        "description": "A test site",
        "author": "Test Author",
        "language": "en"
    }
    
    config_file = temp_site_dir / "config.toml"
    import toml
    with open(config_file, "w", encoding="utf-8") as f:
        toml.dump(config_data, f)
        
    return Config(config_file)


@pytest.fixture
def sample_content(temp_site_dir):
    """Create sample content files."""
    content_dir = temp_site_dir / "content"
    
    # Create a markdown file
    md_file = content_dir / "test.md"
    md_file.write_text("""---
title: Test Post
date: 2024-02-06
---
# Test Post

This is a test post.""")
    
    # Create an HTML file
    html_file = content_dir / "about.html"
    html_file.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>About</title>
</head>
<body>
    <h1>About Page</h1>
    <p>This is the about page.</p>
</body>
</html>""")
    
    return content_dir


@pytest.fixture
def sample_templates(temp_site_dir):
    """Create sample template files."""
    templates_dir = temp_site_dir / "templates"
    
    # Create base template
    base_template = templates_dir / "base.html"
    base_template.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>""")
    
    # Create post template
    post_template = templates_dir / "post.html"
    post_template.write_text("""{% extends "base.html" %}

{% block title %}{{ page.title }}{% endblock %}

{% block content %}
<article>
    <h1>{{ page.title }}</h1>
    <time>{{ page.date }}</time>
    {{ page.content }}
</article>
{% endblock %}""")
    
    return templates_dir


@pytest.fixture
def engine(sample_config):
    """Create a StaticFlow engine instance."""
    return Engine(sample_config)


@pytest.fixture
def async_client():
    """Create an aiohttp test client."""
    import aiohttp
    from aiohttp.test_utils import TestClient
    
    async def _create_client():
        return TestClient(aiohttp.web.Application())
    
    return _create_client 