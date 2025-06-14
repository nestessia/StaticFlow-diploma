import pytest
import logging
from pathlib import Path
from aiohttp import web
from staticflow.admin import AdminPanel
from staticflow.core.config import Config
from staticflow.core.engine import Engine


@pytest.fixture
def config(tmp_path):
    """Создает временную конфигурацию для тестов."""
    config = Config()
    config.set('source_dir', str(tmp_path / "source"))
    config.set('output_dir', str(tmp_path / "output"))
    config.set('static_dir', str(tmp_path / "static"))
    return config


@pytest.fixture
def engine(config):
    """Создает движок для тестов."""
    return Engine(config)


class TestAdminPanel:
    """Тесты для админ-панели."""

    def test_init(self, config, engine):
        """Тест инициализации админ-панели."""
        panel = AdminPanel(config, engine)
        assert panel.config == config
        assert panel.engine == engine

    @pytest.mark.asyncio
    async def test_handle_request_index(self, config, engine):
        """Тест обработки запроса к главной странице."""
        panel = AdminPanel(config, engine)
        request = web.Request(
            "GET", "/admin/",
            protocol=web.HttpVersion11,
            payload_writer=None,
            task=None,
            loop=None
        )
        response = await panel.handle_request(request)
        assert response.status == 200
        assert "text/html" in response.headers["Content-Type"]

    @pytest.mark.asyncio
    async def test_handle_request_api(self, config, engine):
        """Тест обработки API запроса."""
        panel = AdminPanel(config, engine)
        request = web.Request(
            "GET", "/admin/api/pages",
            protocol=web.HttpVersion11,
            payload_writer=None,
            task=None,
            loop=None
        )
        response = await panel.handle_request(request)
        assert response.status == 200
        assert "application/json" in response.headers["Content-Type"]

    def test_copy_static_to_output(self, config, engine, tmp_path):
        """Тест копирования статических файлов."""
        panel = AdminPanel(config, engine)
        static_dir = Path(config.get('static_dir'))
        static_dir.mkdir(parents=True)
        (static_dir / "test.css").write_text("body { color: red; }")
        
        panel.copy_static_to_output()
        assert (Path(config.get('output_dir')) / "static" / "test.css").exists()

    @pytest.mark.asyncio
    async def test_get_pages(self, config, engine, tmp_path):
        """Тест получения списка страниц."""
        panel = AdminPanel(config, engine)
        source_dir = Path(config.get('source_dir'))
        source_dir.mkdir(parents=True)
        (source_dir / "test.md").write_text("# Test Page")
        
        request = web.Request(
            "GET", "/admin/api/pages",
            protocol=web.HttpVersion11,
            payload_writer=None,
            task=None,
            loop=None
        )
        response = await panel.handle_request(request)
        assert response.status == 200
        data = await response.json()
        assert len(data) == 1
        assert data[0]["title"] == "Test Page"

    @pytest.mark.asyncio
    async def test_get_page_content(self, config, engine, tmp_path):
        """Тест получения содержимого страницы."""
        panel = AdminPanel(config, engine)
        source_dir = Path(config.get('source_dir'))
        source_dir.mkdir(parents=True)
        (source_dir / "test.md").write_text("# Test Page\n\nTest content")
        
        request = web.Request(
            "GET", "/admin/api/content/test.md",
            protocol=web.HttpVersion11,
            payload_writer=None,
            task=None,
            loop=None
        )
        response = await panel.handle_request(request)
        assert response.status == 200
        data = await response.json()
        assert "Test Page" in data["content"]
        assert "Test content" in data["content"]

    @pytest.mark.asyncio
    async def test_save_page(self, config, engine, tmp_path):
        """Тест сохранения страницы."""
        panel = AdminPanel(config, engine)
        source_dir = Path(config.get('source_dir'))
        source_dir.mkdir(parents=True)
        
        request = web.Request(
            "POST", "/admin/api/content/test.md",
            protocol=web.HttpVersion11,
            payload_writer=None,
            task=None,
            loop=None
        )
        request._body = b'{"content": "# New Page\\n\\nNew content"}'
        response = await panel.handle_request(request)
        assert response.status == 200
        assert (source_dir / "test.md").exists()
        assert "New Page" in (source_dir / "test.md").read_text() 