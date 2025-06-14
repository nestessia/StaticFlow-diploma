import pytest
import time
from staticflow.parsers.cache import ParserCache


class TestParserCache:
    """Тесты для кэша парсеров."""

    @pytest.fixture
    def cache(self, tmp_path):
        """Фикстура для создания кэша."""
        cache_dir = tmp_path / "cache"
        return ParserCache(str(cache_dir))

    def test_cache_initialization(self):
        """Тест инициализации кэша."""
        cache = ParserCache()
        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()
        assert cache.metadata_file.exists()
        assert isinstance(cache.metadata, dict)
        assert len(cache.metadata) == 0

    def test_cache_set_get(self, cache):
        """Тест сохранения и получения данных из кэша."""
        content = "test content"
        options = {"option1": "value1"}
        value = "cached value"

        cache.set(content, options, value)
        result = cache.get(content, options)
        assert result == value

    def test_cache_invalidation(self, cache):
        """Тест инвалидации кэша."""
        content = "test content"
        options = {"option1": "value1"}
        value = "cached value"

        cache.set(content, options, value)
        cache.invalidate()
        result = cache.get(content, options)
        assert result is None

    def test_cache_ttl(self, cache):
        """Тест времени жизни кэша."""
        content = "test content"
        options = {"option1": "value1"}
        value = "cached value"

        cache.set(content, options, value, ttl=1)
        time.sleep(2)
        result = cache.get(content, options)
        assert result is None

    def test_cache_cleanup(self, cache):
        """Тест очистки кэша."""
        content = "test content"
        options = {"option1": "value1"}
        value = "cached value"

        cache.set(content, options, value, ttl=1)
        time.sleep(2)
        cache.cleanup()
        assert len(cache.metadata) == 0

    def test_cache_stats(self, cache):
        """Тест получения статистики кэша."""
        content = "test content"
        options = {"option1": "value1"}
        value = "cached value"

        cache.set(content, options, value)
        stats = cache.get_stats()
        assert stats["entries"] == 1
        assert stats["total_size"] > 0
        assert str(cache.cache_dir) in stats["cache_dir"]
