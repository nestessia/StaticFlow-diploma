import pytest
from pathlib import Path
import json
from aiohttp import web
from staticflow.admin import AdminPanel


@pytest.fixture
def admin_app(engine):
    """Create admin panel application for testing."""
    admin = AdminPanel(engine.config, engine)
    return admin.app


@pytest.mark.asyncio
async def test_index_page(aiohttp_client, admin_app):
    """Test admin panel index page."""
    client = await aiohttp_client(admin_app)
    resp = await client.get('/')
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Test Site' in text
    assert 'Dashboard' in text


@pytest.mark.asyncio
async def test_content_page(aiohttp_client, admin_app, sample_content):
    """Test content management page."""
    client = await aiohttp_client(admin_app)
    resp = await client.get('/content')
    assert resp.status == 200
    
    text = await resp.text()
    assert 'test.md' in text
    assert 'about.html' in text


@pytest.mark.asyncio
async def test_settings_page(aiohttp_client, admin_app):
    """Test settings page."""
    client = await aiohttp_client(admin_app)
    resp = await client.get('/settings')
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Site Settings' in text
    assert 'Test Site' in text


@pytest.mark.asyncio
async def test_content_api(aiohttp_client, admin_app, temp_site_dir):
    """Test content API endpoints."""
    client = await aiohttp_client(admin_app)
    
    # Test create
    create_data = {
        'action': 'create',
        'path': 'new-post.md',
        'content': '# New Post\n\nThis is a new post.'
    }
    
    resp = await client.post('/api/content',
                           json=create_data)
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    
    # Verify file was created
    new_file = temp_site_dir / 'content' / 'new-post.md'
    assert new_file.exists()
    assert '# New Post' in new_file.read_text()
    
    # Test update
    update_data = {
        'action': 'update',
        'path': 'new-post.md',
        'content': '# Updated Post\n\nThis post was updated.'
    }
    
    resp = await client.post('/api/content',
                           json=update_data)
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    
    # Verify file was updated
    assert '# Updated Post' in new_file.read_text()
    
    # Test delete
    delete_data = {
        'action': 'delete',
        'path': 'new-post.md'
    }
    
    resp = await client.post('/api/content',
                           json=delete_data)
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    
    # Verify file was deleted
    assert not new_file.exists()


@pytest.mark.asyncio
async def test_settings_api(aiohttp_client, admin_app, temp_site_dir):
    """Test settings API endpoint."""
    client = await aiohttp_client(admin_app)
    
    # Update settings
    settings_data = {
        'site_name': 'Updated Site',
        'base_url': 'http://example.com',
        'description': 'Updated description'
    }
    
    resp = await client.post('/api/settings',
                           json=settings_data)
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    
    # Verify config file was updated
    config_file = temp_site_dir / 'config.toml'
    import toml
    config = toml.load(config_file)
    assert config['site_name'] == 'Updated Site'
    assert config['base_url'] == 'http://example.com'
    assert config['description'] == 'Updated description'


@pytest.mark.asyncio
async def test_error_handling(aiohttp_client, admin_app):
    """Test error handling in admin panel."""
    client = await aiohttp_client(admin_app)
    
    # Test invalid content action
    invalid_data = {
        'action': 'invalid',
        'path': 'test.md'
    }
    
    resp = await client.post('/api/content',
                           json=invalid_data)
    assert resp.status == 200  # API always returns 200
    data = await resp.json()
    assert data['status'] == 'error'
    assert 'Invalid action' in data['message']
    
    # Test missing required fields
    resp = await client.post('/api/content',
                           json={'action': 'create'})
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'error'


@pytest.mark.asyncio
async def test_static_files(aiohttp_client, admin_app):
    """Test static file serving in admin panel."""
    client = await aiohttp_client(admin_app)
    
    # Test existing static file
    resp = await client.get('/admin/static/test.css')
    assert resp.status == 404  # File doesn't exist yet
    
    # Create a test static file
    static_dir = Path(__file__).parent.parent / 'staticflow/admin/static'
    static_dir.mkdir(exist_ok=True)
    test_css = static_dir / 'test.css'
    test_css.write_text('body { color: red; }')
    
    # Test again after file creation
    resp = await client.get('/admin/static/test.css')
    assert resp.status == 200
    text = await resp.text()
    assert 'body { color: red; }' in text 