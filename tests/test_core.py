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
        Config({})  # Empty config should raise ValueError


def test_engine_initialization(engine):
    """Test engine initialization."""
    assert engine is not None
    assert isinstance(engine, Engine)


def test_page_creation(sample_content):
    """Test page creation from files."""
    md_file = sample_content / "test.md"
    content = "# Test Post\n\nThis is a test post."
    page = Page(md_file, content, {"title": "Test Post", "date": "2024-02-06"})
    
    assert page.title == "Test Post"
    assert page.metadata["date"] == "2024-02-06"
    assert "Test Post" in page.content
    

def test_site_building(engine, sample_content, sample_templates, temp_site_dir):
    """Test site building process."""
    # Set source and output directories
    engine.site.source_dir = sample_content
    engine.site.output_dir = temp_site_dir / "public"
    engine.site.output_dir.mkdir(exist_ok=True)
    
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
    # Set source and output directories
    engine.site.source_dir = sample_content
    engine.site.output_dir = temp_site_dir / "public"
    engine.site.output_dir.mkdir(exist_ok=True)
    
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
    
    # Create static directory
    static_dir = Path("static")
    static_dir.mkdir(exist_ok=True)
    
    # Create test CSS file
    test_css = static_dir / "test.css"
    test_css.write_text("body { color: red; }")
    
    server = DevServer(engine.config)
    client = await async_client(server.app)
    
    try:
        # Test static file serving
        response = await client.get('/static/test.css')
        assert response.status == 200
        text = await response.text()
        assert "body { color: red; }" in text
        
        # Test SSE endpoint
        response = await client.get('/_dev/events')
        assert response.status == 200
        assert (
            response.headers['Content-Type'] == 'text/event-stream'
        )
    finally:
        await client.close()
        # Cleanup
        test_css.unlink()
        static_dir.rmdir()


def test_error_handling(engine):
    """Test error handling in various scenarios."""
    # Test invalid template
    with pytest.raises(Exception):
        engine.render_template('nonexistent.html', {})
    
    # Test invalid content file
    with pytest.raises(FileNotFoundError):
        Page.from_file(Path('nonexistent.md'))
    
    # Test build with missing directories
    engine.site.source_dir = None
    with pytest.raises(ValueError):
        engine.build() 