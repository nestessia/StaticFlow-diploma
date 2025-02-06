import pytest
from pathlib import Path
from staticflow.core.config import Config
from staticflow.core.engine import Engine
from staticflow.core.page import Page


def test_config_loading(sample_config):
    """Test configuration loading."""
    assert sample_config.get('site_name') == 'Test Site'
    assert sample_config.get('base_url') == 'http://localhost:8000'
    assert sample_config.get('nonexistent', 'default') == 'default'


def test_config_validation():
    """Test configuration validation."""
    with pytest.raises(ValueError):
        Config(None)
        
    with pytest.raises(FileNotFoundError):
        Config(Path('nonexistent.toml'))


def test_engine_initialization(engine):
    """Test engine initialization."""
    assert engine is not None
    assert isinstance(engine, Engine)


def test_page_creation(sample_content):
    """Test page creation from files."""
    md_file = sample_content / "test.md"
    page = Page(md_file)
    
    assert page.title == "Test Post"
    assert page.date == "2024-02-06"
    assert "Test Post" in page.content
    assert page.template == "post.html"


def test_site_building(engine, sample_content, sample_templates, temp_site_dir):
    """Test site building process."""
    # Build the site
    engine.build()
    
    # Check if output files were created
    public_dir = temp_site_dir / "public"
    assert (public_dir / "test.html").exists()
    assert (public_dir / "about.html").exists()
    
    # Check content of generated files
    test_html = (public_dir / "test.html").read_text()
    assert "Test Post" in test_html
    assert "2024-02-06" in test_html
    
    about_html = (public_dir / "about.html").read_text()
    assert "About Page" in about_html


def test_incremental_build(engine, sample_content, temp_site_dir):
    """Test incremental build functionality."""
    # Initial build
    engine.build()
    initial_mtime = (temp_site_dir / "public" / "test.html").stat().st_mtime
    
    # Modify content
    md_file = sample_content / "test.md"
    original_content = md_file.read_text()
    new_content = original_content.replace("test post", "updated post")
    md_file.write_text(new_content)
    
    # Rebuild
    engine.build()
    new_mtime = (temp_site_dir / "public" / "test.html").stat().st_mtime
    
    # Check if file was updated
    assert new_mtime > initial_mtime
    assert "updated post" in (temp_site_dir / "public" / "test.html").read_text()


@pytest.mark.asyncio
async def test_dev_server(engine, async_client):
    """Test development server."""
    from staticflow.cli.server import DevServer
    
    server = DevServer(engine.config)
    client = await async_client()
    
    # Test static file serving
    response = await client.get('/static/test.css')
    assert response.status == 404  # File doesn't exist
    
    # Test SSE endpoint
    response = await client.get('/_dev/events')
    assert response.status == 200
    assert response.headers['Content-Type'] == 'text/event-stream'


def test_error_handling(engine):
    """Test error handling in various scenarios."""
    # Test invalid template
    with pytest.raises(Exception):
        engine.render_template('nonexistent.html', {})
    
    # Test invalid content file
    with pytest.raises(Exception):
        Page(Path('nonexistent.md'))
    
    # Test build with missing directories
    engine.config.set('content_dir', 'nonexistent')
    with pytest.raises(Exception):
        engine.build() 