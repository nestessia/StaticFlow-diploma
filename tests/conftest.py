import pytest
from pathlib import Path
from aiohttp.test_utils import TestClient, TestServer
from staticflow.core.config import Config
from staticflow.core.engine import Engine
from staticflow.core.cache import Cache


@pytest.fixture
def temp_site_dir(tmp_path):
    """Create a temporary site directory."""
    return tmp_path


@pytest.fixture
def sample_config():
    """Create a sample configuration."""
    return Config({
        'site_name': 'Test Site',
        'base_url': 'http://localhost:8000',
        'description': 'A test site'
    })


@pytest.fixture
def sample_content(temp_site_dir):
    """Create sample content files."""
    content_dir = temp_site_dir / 'content'
    content_dir.mkdir(exist_ok=True)
    
    # Create test markdown file
    test_md = content_dir / 'test.md'
    test_md.write_text("""---
title: Test Post
date: 2024-02-06
---

# Test Post

This is a test post.""")
    
    # Create test HTML file
    about_html = content_dir / 'about.html'
    about_html.write_text("""
<h1>About Page</h1>
<p>This is the about page.</p>
""")
    
    return content_dir


@pytest.fixture
def sample_templates(temp_site_dir):
    """Create sample template files."""
    templates_dir = temp_site_dir / 'templates'
    templates_dir.mkdir(exist_ok=True)
    
    # Create base template
    base_html = templates_dir / 'base.html'
    base_html.write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ title }}</title>
</head>
<body>
    {% block content %}{% endblock %}
</body>
</html>""")
    
    # Create post template
    post_html = templates_dir / 'post.html'
    post_html.write_text("""{% extends "base.html" %}
{% block content %}
<article>
    <h1>{{ title }}</h1>
    <time>{{ date }}</time>
    {{ content }}
</article>
{% endblock %}""")
    
    return templates_dir


@pytest.fixture
def engine(sample_config):
    """Create an engine instance."""
    return Engine(sample_config)


@pytest.fixture
def cache_dir():
    """Create a cache directory in current working directory."""
    cache_dir = Path('.cache')
    cache_dir.mkdir(exist_ok=True)
    yield cache_dir
    # Cleanup after tests
    if cache_dir.exists():
        for f in cache_dir.glob('*'):
            f.unlink()
        cache_dir.rmdir()


@pytest.fixture
def cache(cache_dir):
    """Create a cache instance."""
    return Cache(cache_dir)


@pytest.fixture
def async_client(event_loop):
    """Create an async test client."""
    clients = []
    
    async def _get_client(app):
        server = TestServer(app)
        client = TestClient(server)
        await client.start_server()
        clients.append(client)
        return client
        
    yield _get_client
    
    # Cleanup
    for client in clients:
        event_loop.run_until_complete(client.close()) 