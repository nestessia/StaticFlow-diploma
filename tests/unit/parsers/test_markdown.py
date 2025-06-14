import pytest
from staticflow.parsers.markdown import MarkdownParser
import datetime


class TestMarkdownParser:
    """Тесты для парсера Markdown."""

    @pytest.fixture
    def parser(self):
        """Фикстура для создания парсера."""
        return MarkdownParser()

    def test_parse_basic_markdown(self, parser):
        """Тест базового парсинга Markdown."""
        content = "# Заголовок\n\nТекст"
        result = parser.parse(content)
        assert "Заголовок" in result
        assert "Текст" in result

    def test_parse_code_blocks(self, parser):
        """Тест парсинга блоков кода."""
        content = "```python\ndef hello():\n    print('Hello')\n```"
        result = parser.parse(content)
        assert '<div class="highlight">' in result
        assert '<span class="k">def</span>' in result
        assert '<span class="nf">hello</span>' in result

    def test_parse_tables(self, parser):
        """Тест парсинга таблиц."""
        content = """
        | Заголовок 1 | Заголовок 2 |
        |-------------|-------------|
        | Ячейка 1    | Ячейка 2    |
        """
        result = parser.parse(content)
        assert "Заголовок 1" in result
        assert "Заголовок 2" in result
        assert "Ячейка 1" in result
        assert "Ячейка 2" in result

    def test_parse_math(self, parser):
        """Тест парсинга математических формул."""
        content = "$$E = mc^2$$"
        result = parser.parse(content)
        assert "E = mc^2" in result

    def test_add_extension(self, parser):
        """Тест добавления расширения."""
        parser.add_extension("extra", {"option": "value"})
        assert "extra" in parser.extensions
        assert "option" in parser.extension_configs["extra"]

    def test_syntax_highlighting(self, parser):
        """Тест подсветки синтаксиса."""
        parser.set_option("syntax_highlight", True)
        content = "```python\ndef hello():\n    print('Hello')\n```"
        result = parser.parse(content)
        assert "highlight" in result

    def test_parse_with_metadata(self, parser):
        """Тест парсинга с метаданными."""
        content = """---
title: Заголовок
date: 2024-03-20
---

# Заголовок
"""
        result = parser.parse(content)
        assert '<h1 id="_1">Заголовок' in result
        assert '<a class="headerlink"' in result

    def test_get_metadata(self, parser):
        """Тест получения метаданных."""
        content = """---
title: Тест
date: 2024-03-20
---

# Заголовок
"""
        metadata = parser.get_metadata(content)
        assert metadata["title"] == "Тест"
        assert isinstance(metadata["date"], datetime.date)
        assert metadata["date"].year == 2024
        assert metadata["date"].month == 3
        assert metadata["date"].day == 20

    def test_validate_valid_content(self, parser):
        """Тест валидации корректного контента."""
        content = "# Заголовок\n\nЭто параграф."
        assert parser.validate(content) is True

    def test_validate_invalid_content(self, parser):
        """Тест валидации некорректного контента."""
        content = None
        assert parser.validate(content) is False 