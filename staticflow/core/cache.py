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
        self._save_metadata()

    def _get_cache_key(self, key: str, namespace: str = 'default') -> str:
        """Generate a cache key."""
        return hashlib.sha256(f"{namespace}:{key}".encode()).hexdigest()

    def _get_cache_path(self, cache_key: str) -> Path:
        """Get cache file path."""
        return self.cache_dir / f"{cache_key}.cache"

    def get(self, key: str, namespace: str = 'default') -> Optional[Any]:
        """Get a value from cache."""
        cache_key = self._get_cache_key(key, namespace)

        if cache_key in self._memory_cache:
            metadata = self._metadata.get(cache_key, {})
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    self.delete(key, namespace)
                    return None
            return self._memory_cache[cache_key]

        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            metadata = self._metadata.get(cache_key, {})
            if metadata.get('expires'):
                expires = datetime.fromisoformat(metadata['expires'])
                if expires <= datetime.now():
                    self.delete(key, namespace)
                    return None

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

        self._memory_cache[cache_key] = value

        cache_path = self._get_cache_path(cache_key)
        with cache_path.open('wb') as f:
            pickle.dump(value, f)

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

        self._memory_cache.pop(cache_key, None)

        cache_path = self._get_cache_path(cache_key)
        if cache_path.exists():
            cache_path.unlink()

        self._metadata.pop(cache_key, None)
        self._save_metadata()

    def clear(self, namespace: Optional[str] = None) -> None:
        """Clear cache."""
        if namespace:
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
