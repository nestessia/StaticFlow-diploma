import pytest
from pathlib import Path
import tempfile
from datetime import datetime, date
from staticflow.core.page import Page
from staticflow.core.config import Config


class TestPage:
    """Тесты для класса Page."""

    @pytest.fixture
    def config_path(self, tmp_path):
        """Фикстура для создания временного файла конфигурации."""
        config_file = tmp_path / "config.toml"
        config_content = """
default_language = "en"
USE_LANGUAGE_PREFIXES = true
EXCLUDE_DEFAULT_LANG_PREFIX = true
CLEAN_URLS = true
PRESERVE_DIRECTORY_STRUCTURE = true
"""
        config_file.write_text(config_content)
        return config_file

    @pytest.fixture
    def config(self, config_path):
        """Фикстура для создания конфигурации."""
        return Config(config_path)

    @pytest.fixture
    def temp_page_file(self):
        """Фикстура для создания временного файла страницы."""
        with tempfile.NamedTemporaryFile(suffix=".md", delete=False, mode='w', encoding='utf-8') as f:
            content = """---
title: Test Page
date: 2024-03-20
language: en
template: default.html
---

# Test Content
This is a test page content.
"""
            f.write(content)
            return Path(f.name)

    @pytest.fixture
    def page(self):
        """Фикстура для создания страницы."""
        return Page(
            source_path=Path("content/test.md"),
            content="# Test Content\nThis is a test page content.",
            metadata={
                "title": "Test Page",
                "date": date.today(),
                "slug": "test",
                "category": "blog"
            }
        )

    def test_init(self, page):
        """Тест инициализации страницы."""
        assert page.source_path == Path("content/test.md")
        assert page.metadata["title"] == "Test Page"
        assert isinstance(page.metadata["date"], date)
        assert page.metadata["slug"] == "test"
        assert page.metadata["category"] == "blog"

    def test_from_file(self, tmp_path):
        """Тест создания страницы из файла."""
        # Создаем временный файл
        content = """---
title: Test Page
date: 2024-03-20
slug: test
category: blog
---

Test content
"""
        file_path = tmp_path / "test.md"
        file_path.write_text(content)

        # Создаем страницу из файла
        page = Page.from_file(file_path)

        # Проверяем метаданные
        assert page.metadata["title"] == "Test Page"
        assert isinstance(page.metadata["date"], date)
        assert page.metadata["date"].year == 2024
        assert page.metadata["date"].month == 3
        assert page.metadata["date"].day == 20
        assert page.metadata["slug"] == "test"
        assert page.metadata["category"] == "blog"
        assert page.content == "Test content"

    def test_from_file_nonexistent(self):
        """Тест создания страницы из несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            Page.from_file(Path("nonexistent.md"))

    def test_title(self, page):
        """Тест получения заголовка страницы."""
        assert page.title == "Test Page"
        page.metadata = {}
        assert page.title == page.source_path.stem

    def test_url(self, page):
        """Тест получения URL страницы."""
        assert page.url == ""

    def test_set_output_path(self, page):
        """Тест установки пути вывода."""
        output_path = Path("output/test.html")
        page.set_output_path(output_path)
        assert page.output_path == output_path

    def test_set_rendered_content(self, page):
        """Тест установки отрендеренного контента."""
        content = "<h1>Test</h1>"
        page.set_rendered_content(content)
        assert page.rendered_content == content
        assert isinstance(page.modified_at, datetime)

    def test_update_metadata(self, page):
        """Тест обновления метаданных."""
        new_metadata = {"author": "Test Author"}
        page.update_metadata(new_metadata)
        assert page.metadata["author"] == "Test Author"
        assert isinstance(page.modified_at, datetime)

    def test_get_available_translations(self, tmp_path):
        """Тест получения доступных переводов."""
        # Создаем временную структуру директорий
        content_dir = tmp_path / "content"
        content_dir.mkdir()
        en_dir = content_dir / "en"
        en_dir.mkdir()
        ru_dir = content_dir / "ru"
        ru_dir.mkdir()
        
        # Создаем файлы
        en_file = en_dir / "test.md"
        en_file.write_text("# Test")
        ru_file = ru_dir / "test.md"
        ru_file.write_text("# Тест")
        
        # Создаем страницу
        page = Page.from_file(en_file)
        translations = page.get_available_translations()
        assert "ru" in translations

    def test_render(self, page, tmp_path):
        """Тест рендеринга страницы."""
        # Создаем временный шаблон
        template_dir = tmp_path / "templates"
        template_dir.mkdir()
        template_path = template_dir / "default.html"
        template_path.write_text("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{{ page.title }}</title>
        </head>
        <body>
            <h1>{{ page.title }}</h1>
            <div class="content">
                {{ page.content }}
            </div>
        </body>
        </html>
        """)

        # Рендерим страницу
        rendered = page.render()
        assert "Test Content" in rendered
        assert "This is a test page content" in rendered

    def test_render_without_template(self, page):
        """Тест рендеринга страницы без шаблона."""
        page.metadata = {}
        rendered = page.render()
        assert "Test Content" in rendered
        assert "<!DOCTYPE html>" not in rendered 