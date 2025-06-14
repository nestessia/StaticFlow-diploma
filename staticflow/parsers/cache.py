from typing import Any, Dict, Optional
import hashlib
import json
import time
from pathlib import Path
import pickle


class ParserCache:
    """Система кэширования для парсеров."""

    def __init__(self, cache_dir: str = ".cache/parsers"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.metadata_file = self.cache_dir / "metadata.json"
        if not self.metadata_file.exists():
            self.metadata_file.touch()
        self.metadata = self._load_metadata()

    def _load_metadata(self) -> Dict[str, Any]:
        """Загружает метаданные кэша."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return {}
        return {}

    def _save_metadata(self) -> None:
        """Сохраняет метаданные кэша."""
        with open(self.metadata_file, 'w') as f:
            json.dump(self.metadata, f)

    def _get_cache_key(self, content: str, options: Dict[str, Any]) -> str:
        """Генерирует ключ кэша на основе контента и опций."""
        data = f"{content}{json.dumps(options, sort_keys=True)}"
        return hashlib.md5(data.encode()).hexdigest()

    def _get_cache_path(self, key: str) -> Path:
        """Возвращает путь к файлу кэша."""
        return self.cache_dir / f"{key}.pkl"

    def get(self, content: str, options: Dict[str, Any]) -> Optional[Any]:
        """Получает данные из кэша."""
        key = self._get_cache_key(content, options)
        cache_path = self._get_cache_path(key)

        if not cache_path.exists():
            return None

        if key not in self.metadata:
            return None

        # Проверка времени жизни кэша
        cache_time = time.time() - self.metadata[key]['timestamp']
        if cache_time > self.metadata[key]['ttl']:
            self.invalidate(key)
            return None

        try:
            with open(cache_path, 'rb') as f:
                return pickle.load(f)
        except (pickle.UnpicklingError, IOError):
            return None

    def set(
        self,
        content: str,
        options: Dict[str, Any],
        value: Any,
        ttl: int = 3600
    ) -> None:
        """Сохраняет данные в кэш."""
        key = self._get_cache_key(content, options)
        cache_path = self._get_cache_path(key)

        # Сохранение данных
        with open(cache_path, 'wb') as f:
            pickle.dump(value, f)

        # Обновление метаданных
        self.metadata[key] = {
            'timestamp': time.time(),
            'ttl': ttl,
            'options': options
        }
        self._save_metadata()

    def invalidate(self, key: Optional[str] = None) -> None:
        """Инвалидирует кэш."""
        if key:
            # Инвалидация конкретного ключа
            cache_path = self._get_cache_path(key)
            if cache_path.exists():
                cache_path.unlink()
            if key in self.metadata:
                del self.metadata[key]
        else:
            # Инвалидация всего кэша
            for file in self.cache_dir.glob("*.pkl"):
                file.unlink()
            self.metadata.clear()
        self._save_metadata()

    def cleanup(self) -> None:
        """Очищает устаревшие записи кэша."""
        current_time = time.time()
        keys_to_remove = []

        for key, data in self.metadata.items():
            if current_time - data['timestamp'] > data['ttl']:
                keys_to_remove.append(key)

        for key in keys_to_remove:
            self.invalidate(key)

    def get_stats(self) -> Dict[str, Any]:
        """Возвращает статистику кэша."""
        total_size = sum(
            f.stat().st_size for f in self.cache_dir.glob("*.pkl")
        )
        return {
            'entries': len(self.metadata),
            'total_size': total_size,
            'cache_dir': str(self.cache_dir)
        } 