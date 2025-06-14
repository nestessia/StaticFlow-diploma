import pytest
from pathlib import Path
from staticflow.core.router import Router
from staticflow.core.category import Category


class TestRouter:
    """Тесты для класса Router."""

    @pytest.fixture
    def config(self):
        """Фикстура для создания конфигурации."""
        return {
            "default_language": "en",
            "USE_LANGUAGE_PREFIXES": True,
            "EXCLUDE_DEFAULT_LANG_PREFIX": True,
            "CLEAN_URLS": True,
            "PRESERVE_DIRECTORY_STRUCTURE": True
        }

    @pytest.fixture
    def router(self, config):
        """Фикстура для создания роутера."""
        return Router(config)

    def test_init(self, config):
        """Тест инициализации роутера."""
        router = Router(config)
        assert router.default_language == "en"
        assert router.use_language_prefixes is True
        assert router.exclude_default_lang_prefix is True
        assert router.use_clean_urls is True
        assert router.preserve_directory_structure is True

    def test_update_config(self, router):
        """Тест обновления конфигурации."""
        new_config = {
            "default_language": "ru",
            "USE_LANGUAGE_PREFIXES": False,
            "EXCLUDE_DEFAULT_LANG_PREFIX": False,
            "CLEAN_URLS": False,
            "PRESERVE_DIRECTORY_STRUCTURE": False
        }
        router.update_config(new_config)
        assert router.default_language == "ru"
        assert router.use_language_prefixes is False
        assert router.exclude_default_lang_prefix is False
        assert router.use_clean_urls is False
        assert router.preserve_directory_structure is False

    def test_get_url_page(self, router):
        """Тест получения URL для страницы."""
        metadata = {
            "slug": "test-page",
            "category": "blog"
        }
        url = router.get_url("page", metadata)
        assert url == "/blog/test-page"

    def test_get_url_post(self, router):
        """Тест получения URL для поста."""
        metadata = {
            "slug": "test-post",
            "category": "news"
        }
        url = router.get_url("post", metadata)
        assert url == "/news/test-post"

    def test_get_url_tag(self, router):
        """Тест получения URL для тега."""
        metadata = {"name": "python"}
        url = router.get_url("tag", metadata)
        assert url == "/python"

    def test_get_url_category(self, router):
        """Тест получения URL для категории."""
        metadata = {"category_path": "blog"}
        url = router.get_url("category", metadata)
        assert url == "/blog"

    def test_get_url_index(self, router):
        """Тест получения URL для индексной страницы."""
        metadata = {"slug": "index"}
        url = router.get_url("page", metadata)
        assert url == "/"

    def test_get_save_as_page(self, router):
        """Тест получения пути сохранения для страницы."""
        metadata = {
            "slug": "test-page",
            "category": "blog"
        }
        save_as = router.get_save_as("page", metadata)
        assert save_as == "blog/test-page/index.html"

    def test_get_save_as_post(self, router):
        """Тест получения пути сохранения для поста."""
        metadata = {
            "slug": "test-post",
            "category": "news"
        }
        save_as = router.get_save_as("post", metadata)
        assert save_as == "news/test-post/index.html"

    def test_get_save_as_tag(self, router):
        """Тест получения пути сохранения для тега."""
        metadata = {"name": "python"}
        save_as = router.get_save_as("tag", metadata)
        assert save_as == "python/index.html"

    def test_get_save_as_category(self, router):
        """Тест получения пути сохранения для категории."""
        metadata = {"category_path": "blog"}
        save_as = router.get_save_as("category", metadata)
        assert save_as == "blog/index.html"

    def test_get_save_as_index(self, router):
        """Тест получения пути сохранения для индексной страницы."""
        metadata = {"slug": "index"}
        save_as = router.get_save_as("page", metadata)
        assert save_as == "index.html"

    def test_get_output_path(self, router):
        """Тест получения пути вывода."""
        output_dir = Path("output")
        metadata = {
            "slug": "test-page",
            "category": "blog",
            "source_path": "content/blog/test-page.md"
        }
        output_path = router.get_output_path(output_dir, "page", metadata)
        assert str(output_path).replace("\\", "/") == "output/blog/test-page/index.html"

    def test_get_output_path_with_directory_structure(self, router):
        """Тест получения пути вывода с сохранением структуры директорий."""
        output_dir = Path("output")
        metadata = {
            "slug": "test-page",
            "source_path": "content/blog/2024/test-page.md",
            "category": "blog"
        }
        output_path = router.get_output_path(output_dir, "page", metadata)
        assert str(output_path).replace("\\", "/") == "output/blog/2024/test-page/index.html"

    def test_get_category_path(self, router):
        """Тест получения пути категории."""
        category = Category("blog")
        path = router._get_category_path(category)
        assert path == "blog"

        path = router._get_category_path("news")
        assert path == "news"

        path = router._get_category_path(["tech"])
        assert path == "tech"

    def test_clear_cache(self, router):
        """Тест очистки кэша."""
        metadata = {"slug": "test-page"}
        router.get_url("page", metadata)
        router.get_save_as("page", metadata)
        
        assert len(router._url_cache) > 0
        assert len(router._save_as_cache) > 0
        
        router.clear_cache()
        
        assert len(router._url_cache) == 0
        assert len(router._save_as_cache) == 0 