import pytest
from pathlib import Path
import time
from datetime import timedelta
from staticflow.core.cache import Cache


@pytest.fixture
def cache_dir(temp_site_dir):
    """Create a temporary cache directory."""
    cache_dir = temp_site_dir / '.cache'
    cache_dir.mkdir()
    return cache_dir


@pytest.fixture
def cache(cache_dir):
    """Create a cache instance."""
    return Cache(cache_dir)


def test_cache_initialization(cache_dir):
    """Test cache initialization."""
    cache = Cache(cache_dir)
    assert cache.cache_dir == cache_dir
    assert cache.cache_dir.exists()
    
    # Test metadata file creation
    metadata_file = cache_dir / 'metadata.json'
    assert metadata_file.exists()


def test_cache_basic_operations(cache):
    """Test basic cache operations."""
    # Test set and get
    cache.set('test_key', 'test_value')
    assert cache.get('test_key') == 'test_value'
    
    # Test default value
    assert cache.get('nonexistent') is None
    
    # Test delete
    cache.delete('test_key')
    assert cache.get('test_key') is None


def test_cache_namespaces(cache):
    """Test cache namespaces."""
    cache.set('key', 'value1', namespace='ns1')
    cache.set('key', 'value2', namespace='ns2')
    
    assert cache.get('key', namespace='ns1') == 'value1'
    assert cache.get('key', namespace='ns2') == 'value2'
    
    # Clear specific namespace
    cache.clear(namespace='ns1')
    assert cache.get('key', namespace='ns1') is None
    assert cache.get('key', namespace='ns2') == 'value2'


def test_cache_expiration(cache):
    """Test cache expiration."""
    # Set with expiration
    cache.set('expire_key', 'value', expires=timedelta(seconds=1))
    assert cache.get('expire_key') == 'value'
    
    # Wait for expiration
    time.sleep(1.1)
    assert cache.get('expire_key') is None


def test_cache_complex_objects(cache):
    """Test caching complex objects."""
    test_data = {
        'string': 'test',
        'number': 42,
        'list': [1, 2, 3],
        'dict': {'key': 'value'},
        'set': {1, 2, 3}
    }
    
    cache.set('complex', test_data)
    retrieved = cache.get('complex')
    
    assert retrieved == test_data
    assert isinstance(retrieved['set'], set)


def test_cache_memory_persistence(cache):
    """Test memory cache persistence."""
    cache.set('memory_test', 'value')
    
    # Create new cache instance
    new_cache = Cache(cache.cache_dir)
    assert new_cache.get('memory_test') == 'value'


def test_cache_stats(cache):
    """Test cache statistics."""
    # Add test data
    cache.set('key1', 'value1', namespace='ns1')
    cache.set('key2', 'value2', namespace='ns1')
    cache.set('key3', 'value3', namespace='ns2')
    cache.set('key4', 'value4', namespace='ns2', 
             expires=timedelta(seconds=-1))  # Already expired
    
    stats = cache.get_stats()
    
    assert stats['total_entries'] == 4
    assert stats['memory_entries'] == 4
    assert stats['size_bytes'] > 0
    assert len(stats['namespaces']) == 2
    assert stats['namespaces']['ns1']['entries'] == 2
    assert stats['namespaces']['ns2']['entries'] == 2
    assert stats['namespaces']['ns2']['expired'] == 1


def test_cache_cleanup(cache):
    """Test cache cleanup."""
    # Add test data with different expirations
    cache.set('key1', 'value1')  # No expiration
    cache.set('key2', 'value2', expires=timedelta(seconds=-1))  # Expired
    cache.set('key3', 'value3', expires=timedelta(hours=1))  # Not expired
    
    cleaned = cache.cleanup()
    assert cleaned == 1
    
    assert cache.get('key1') is not None
    assert cache.get('key2') is None
    assert cache.get('key3') is not None


def test_cache_clear(cache):
    """Test cache clearing."""
    # Add test data
    cache.set('key1', 'value1', namespace='ns1')
    cache.set('key2', 'value2', namespace='ns2')
    
    # Clear all cache
    cache.clear()
    
    assert cache.get('key1', namespace='ns1') is None
    assert cache.get('key2', namespace='ns2') is None
    assert len(list(cache.cache_dir.glob('*.cache'))) == 0


def test_cache_error_handling(cache):
    """Test cache error handling."""
    # Test invalid pickle data
    cache_key = cache._get_cache_key('invalid')
    cache_path = cache._get_cache_path(cache_key)
    
    # Write invalid data
    cache_path.write_bytes(b'invalid pickle data')
    
    # Should return None for corrupted data
    assert cache.get('invalid') is None
    
    # Test file permission errors
    cache_path.chmod(0o000)  # Remove all permissions
    try:
        cache.set('permission_test', 'value')
        assert cache.get('permission_test') is None
    finally:
        cache_path.chmod(0o666)  # Restore permissions 