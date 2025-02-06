import hashlib
import json
import pickle
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime, timedelta


class Cache:
    """Cache system for StaticFlow."""
    
    def __init__(self, cache_dir: Path):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self._memory_cache: Dict[str, Any] = {}
        self._metadata: Dict[str, Dict] = self._load_metadata()
        self._save_metadata()  # Save empty metadata file if it doesn't exist
        
    def _load_metadata(self) -> Dict[str, Dict]:
        """Load cache metadata."""
        metadata_file = self.cache_dir / 'metadata.json'
        if metadata_file.exists():
            return json.loads(metadata_file.read_text())
        return {}
        
    def _save_metadata(self) -> None:
        """Save cache metadata."""
        metadata_file = self.cache_dir / 'metadata.json'
        metadata_file.write_text(json.dumps(self._metadata))
        
    def _get_cache_key(self, key: str, namespace: str = 'default') -> str:
        """Generate a cache key."""
        return hashlib.sha256(f"{namespace}:{key}".encode()).hexdigest()
        
    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.cache"
        
    def get(self, key: str, namespace: str = 'default') -> Optional[Any]:
        """Get a value from cache."""
        cache_key = self._get_cache_key(key, namespace)
        
        # Check memory cache first
        if cache_key in self._memory_cache:
            # Check expiration for memory cache
            metadata = self._metadata.get(cache_key, {})
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    self.delete(key, namespace)
                    return None
            return self._memory_cache[cache_key]
            
        # Check file cache
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            # Check expiration
            metadata = self._metadata.get(cache_key, {})
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    self.delete(key, namespace)
                    return None
                    
            # Load from cache file
            try:
                with cache_path.open('rb') as f:
                    value = pickle.load(f)
                    self._memory_cache[cache_key] = value
                    return value
            except (pickle.PickleError, EOFError):
                self.delete(key, namespace)
                return None
                
        return None
        
    def set(self, key: str, value: Any, 
            namespace: str = 'default',
            expires: Optional[timedelta] = None) -> None:
        """Set a value in cache."""
        cache_key = self._get_cache_key(key, namespace)
        
        # Save to memory cache
        self._memory_cache[cache_key] = value
        
        # Save to file cache
        cache_path = self._get_cache_path(cache_key)
        with cache_path.open('wb') as f:
            pickle.dump(value, f)
            
        # Update metadata
        self._metadata[cache_key] = {
            'key': key,
            'namespace': namespace,
            'created': datetime.now().isoformat(),
            'expires': (datetime.now() + expires).isoformat() if expires else None
        }
        self._save_metadata()
        
    def delete(self, key: str, namespace: str = 'default') -> None:
        """Delete a value from cache."""
        cache_key = self._get_cache_key(key, namespace)
        
        # Remove from memory cache
        self._memory_cache.pop(cache_key, None)
        
        # Remove cache file
        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()
            
        # Update metadata
        self._metadata.pop(cache_key, None)
        self._save_metadata()
        
    def clear(self, namespace: Optional[str] = None) -> None:
        """Clear cache."""
        if namespace:
            # Clear specific namespace
            keys_to_delete = []
            for cache_key, metadata in self._metadata.items():
                if metadata['namespace'] == namespace:
                    keys_to_delete.append((metadata['key'], namespace))
                    
            for key, ns in keys_to_delete:
                self.delete(key, ns)
        else:
            # Clear all cache
            self._memory_cache.clear()
            for cache_file in self.cache_dir.glob('*.cache'):
                cache_file.unlink()
            self._metadata.clear()
            self._save_metadata()
            
    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'total_entries': len(self._metadata),
            'memory_entries': len(self._memory_cache),
            'size_bytes': sum(f.stat().st_size 
                            for f in self.cache_dir.glob('*.cache')),
            'namespaces': {}
        }
        
        # Collect namespace stats
        for metadata in self._metadata.values():
            namespace = metadata['namespace']
            if namespace not in stats['namespaces']:
                stats['namespaces'][namespace] = {
                    'entries': 0,
                    'expired': 0
                }
                
            stats['namespaces'][namespace]['entries'] += 1
            
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    stats['namespaces'][namespace]['expired'] += 1
                    
        return stats
        
    def cleanup(self) -> int:
        """Clean up expired cache entries."""
        cleaned = 0
        keys_to_delete = []
        
        for cache_key, metadata in self._metadata.items():
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    keys_to_delete.append(
                        (metadata['key'], metadata['namespace'])
                    )
                    
        for key, namespace in keys_to_delete:
            self.delete(key, namespace)
            cleaned += 1
            
        return cleaned 