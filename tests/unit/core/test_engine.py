import pytest
from pathlib import Path
from datetime import datetime
from staticflow.core.engine import Engine
from staticflow.core.config import Config
from staticflow.core.page import Page
from staticflow.plugins.base import Plugin


class TestPlugin(Plugin):
    """Тестовый плагин для проверки функциональности Engine."""
    
    def initialize(self):
        """Инициализация плагина."""
        self.processed = False
        self.pre_build_called = False
        self.post_build_called = False

    def process_content(self, content: str) -> str:
        """Обработка контента."""
        self.processed = True
        return f"<!-- Processed by TestPlugin -->\n{content}"

    def pre_build(self, site):
        """Действия перед сборкой."""
        self.pre_build_called = True

    def post_build(self, site):
        """Действия после сборки."""
        self.post_build_called = True


class TestEngine:
    """Тесты для класса Engine."""

    @pytest.fixture
    def config_path(self, tmp_path):
        """Фикстура для создания временного файла конфигурации."""
        config_file = tmp_path / "config.toml"
        config_content = """
site_name = "Test Site"
base_url = "http://example.com"
default_language = "en"
USE_LANGUAGE_PREFIXES = true
EXCLUDE_DEFAULT_LANG_PREFIX = true
CLEAN_URLS = true
PRESERVE_DIRECTORY_STRUCTURE = true
template_dir = "templates"
"""
        config_file.write_text(config_content)
        return config_file

    @pytest.fixture
    def engine(self, config_path):
        """Фикстура для создания движка."""
        return Engine(config_path)

    @pytest.fixture
    def test_dirs(self, tmp_path):
        """Фикстура для создания тестовых директорий."""
        source_dir = tmp_path / "source"
        output_dir = tmp_path / "output"
        templates_dir = tmp_path / "templates"
        static_dir = tmp_path / "static"

        # Создаем структуру директорий
        source_dir.mkdir()
        output_dir.mkdir()
        templates_dir.mkdir()
        static_dir.mkdir()

        # Создаем тестовый шаблон
        template_file = templates_dir / "default.html"
        template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
    {{ page_head_content }}
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>
"""
        template_file.write_text(template_content)

        # Создаем тестовую страницу
        page_file = source_dir / "test.md"
        page_content = """---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
"""
        page_file.write_text(page_content)

        # Создаем статические файлы
        static_file = static_dir / "test.css"
        static_file.write_text("body { color: black; }")

        return {
            "source_dir": source_dir,
            "output_dir": output_dir,
            "templates_dir": templates_dir,
            "static_dir": static_dir
        }

    def test_init_with_config_path(self, config_path):
        """Тест инициализации с путем к конфигурации."""
        engine = Engine(config_path)
        assert isinstance(engine.config, Config)
        assert engine.config.get("site_name") == "Test Site"

    def test_init_with_config_object(self, config_path):
        """Тест инициализации с объектом конфигурации."""
        config = Config(config_path)
        engine = Engine(config)
        assert engine.config == config

    def test_init_with_invalid_config(self):
        """Тест инициализации с неверной конфигурацией."""
        with pytest.raises(TypeError):
            Engine(123)

    def test_add_plugin(self, engine):
        """Тест добавления плагина."""
        plugin = TestPlugin()
        engine.add_plugin(plugin)
        assert plugin in engine.plugins
        assert plugin.engine == engine

    def test_get_plugin(self, engine):
        """Тест получения плагина по имени."""
        plugin = TestPlugin()
        plugin.metadata = type('Metadata', (), {'name': 'test'})()
        engine.add_plugin(plugin)
        assert engine.get_plugin('test') == plugin
        assert engine.get_plugin('nonexistent') is None

    def test_initialize(self, engine, test_dirs):
        """Тест инициализации директорий."""
        engine.initialize(
            test_dirs["source_dir"],
            test_dirs["output_dir"],
            test_dirs["templates_dir"]
        )
        assert engine.site.source_dir == test_dirs["source_dir"]
        assert engine.site.output_dir == test_dirs["output_dir"]
        assert engine.site.template_dir == test_dirs["templates_dir"]


    def test_clean(self, engine, test_dirs):
        """Тест очистки выходной директории."""
        # Создаем тестовые файлы
        test_file = test_dirs["output_dir"] / "test.html"
        test_file.write_text("test")
        static_dir = test_dirs["output_dir"] / "static"
        static_dir.mkdir()
        static_file = static_dir / "test.css"
        static_file.write_text("test")

        # Очищаем директорию
        engine.initialize(
            test_dirs["source_dir"],
            test_dirs["output_dir"],
            test_dirs["templates_dir"]
        )
        engine.clean()

        # Проверяем, что файлы удалены
        assert not test_file.exists()
        assert not static_dir.exists()

    def test_load_page_from_file(self, engine, test_dirs):
        """Тест загрузки страницы из файла."""
        page_file = test_dirs["source_dir"] / "test.md"
        page = engine.load_page_from_file(page_file)
        assert isinstance(page, Page)
        assert page.metadata["title"] == "Test Page"
        assert "Test Content" in page.content