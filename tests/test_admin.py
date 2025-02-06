import pytest
from pathlib import Path
import shutil
from staticflow.admin import AdminPanel


@pytest.fixture
def admin_app(engine):
    """Create admin panel app for testing."""
    # Create admin static directory
    static_dir = Path(__file__).parent.parent / 'staticflow/admin/static'
    static_dir.mkdir(parents=True, exist_ok=True)
    
    try:
        admin = AdminPanel(engine.config, engine)
        app = admin.app
        app.config = engine.config  # Store config in app for tests
        app.engine = engine  # Store engine in app for tests
        return app
    finally:
        # Cleanup will be handled by individual tests
        pass


@pytest.mark.asyncio
async def test_index_page(async_client, admin_app):
    """Test admin panel index page."""
    client = await async_client(admin_app)
    resp = await client.get('/')
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Test Site' in text
    assert 'Dashboard' in text


@pytest.mark.asyncio
async def test_content_page(async_client, admin_app, sample_content):
    """Test content management page."""
    client = await async_client(admin_app)
    
    # Create content directory and test files
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    
    try:
        # Create test files
        test_file = content_dir / 'test.md'
        test_file.write_text('# Test\n\nTest content')
        about_file = content_dir / 'about.html'
        about_file.write_text('<h1>About</h1>')
        
        resp = await client.get('/content')
        assert resp.status == 200
        
        text = await resp.text()
        assert 'test.md' in text
        assert 'about.html' in text
    finally:
        # Cleanup
        if content_dir.exists():
            shutil.rmtree(content_dir)


@pytest.mark.asyncio
async def test_settings_page(async_client, admin_app):
    """Test settings page."""
    client = await async_client(admin_app)
    resp = await client.get('/settings')
    assert resp.status == 200
    
    text = await resp.text()
    assert 'Site Settings' in text
    assert 'Test Site' in text


@pytest.mark.asyncio
async def test_content_api(async_client, admin_app, temp_site_dir):
    """Test content API endpoints."""
    client = await async_client(admin_app)
    
    # Create content directory
    content_dir = Path('content')
    content_dir.mkdir(exist_ok=True)
    
    try:
        # Test create
        create_data = {
            'action': 'create',
            'path': 'new-post.md',
            'content': '# New Post\n\nThis is a new post.'
        }
        
        resp = await client.post('/api/content', json=create_data)
        assert resp.status == 200
        data = await resp.json()
        assert data['status'] == 'ok'
        
        # Verify file was created
        new_file = content_dir / 'new-post.md'
        assert new_file.exists()
        assert '# New Post' in new_file.read_text()
        
        # Test update
        update_data = {
            'action': 'update',
            'path': 'new-post.md',
            'content': '# Updated Post\n\nThis post was updated.'
        }
        
        resp = await client.post('/api/content', json=update_data)
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
        
        resp = await client.post('/api/content', json=delete_data)
        assert resp.status == 200
        data = await resp.json()
        assert data['status'] == 'ok'
        
        # Verify file was deleted
        assert not new_file.exists()
    finally:
        # Cleanup
        if content_dir.exists():
            shutil.rmtree(content_dir)


@pytest.mark.asyncio
async def test_settings_api(async_client, admin_app, temp_site_dir):
    """Test settings API endpoint."""
    client = await async_client(admin_app)
    
    # Update settings
    settings_data = {
        'site_name': 'Updated Site',
        'base_url': 'http://example.com',
        'description': 'Updated description'
    }
    
    resp = await client.post('/api/settings', json=settings_data)
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'ok'
    
    # Verify config was updated
    assert admin_app.config.get('site_name') == 'Updated Site'
    assert admin_app.config.get('base_url') == 'http://example.com'
    assert admin_app.config.get('description') == 'Updated description'


@pytest.mark.asyncio
async def test_error_handling(async_client, admin_app):
    """Test error handling in admin panel."""
    client = await async_client(admin_app)
    
    # Test invalid content action
    invalid_data = {
        'action': 'invalid',
        'path': 'test.md'
    }
    
    resp = await client.post('/api/content', json=invalid_data)
    assert resp.status == 200  # API always returns 200
    data = await resp.json()
    assert data['status'] == 'error'
    assert 'Invalid action' in data['message']
    
    # Test missing required fields
    resp = await client.post('/api/content', json={'action': 'create'})
    assert resp.status == 200
    data = await resp.json()
    assert data['status'] == 'error'


@pytest.mark.asyncio
async def test_static_files(async_client, admin_app):
    """Test static file serving in admin panel."""
    client = await async_client(admin_app)
    
    # Get admin static directory
    static_dir = Path(__file__).parent.parent / 'staticflow/admin/static'
    
    # Create test CSS file
    test_css = static_dir / 'test.css'
    test_css.write_text('body { color: red; }')
    
    try:
        # Test static file serving
        resp = await client.get('/admin/static/test.css')
        assert resp.status == 200
        text = await resp.text()
        assert 'body { color: red; }' in text
    finally:
        # Cleanup - wait for file to be released
        import time
        for _ in range(3):  # Try a few times
            try:
                if test_css.exists():
                    test_css.unlink()
                break
            except PermissionError:
                time.sleep(0.1)  # Wait a bit
        
        # Remove static directory if empty
        if static_dir.exists() and not any(static_dir.iterdir()):
            static_dir.rmdir() 