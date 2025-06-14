import pytest
from staticflow.parsers.html import HTMLParser


class TestHTMLParser:
    """Тесты для парсера HTML."""

    @pytest.fixture
    def parser(self):
        """Фикстура для создания парсера."""
        return HTMLParser()

    def test_parse_basic_html(self, parser):
        """Тест базового парсинга HTML."""
        content = "<div><p>Текст</p></div>"
        result = parser.parse(content)
        assert "Текст" in result
        assert "<div>" in result
        assert "<p>" in result

    def test_parse_without_beautify(self):
        """Тест парсинга без форматирования."""
        parser = HTMLParser(beautify=False)
        content = "<div><p>Текст</p></div>"
        result = parser.parse(content)
        assert result == content

    def test_parse_with_metadata(self, parser):
        """Тест парсинга HTML с метаданными."""
        content = """
        <html>
        <head>
            <title>Тестовая страница</title>
            <meta name="date" content="2024-03-20">
        </head>
        <body>
            <h1>Заголовок</h1>
        </body>
        </html>
        """
        result = parser.parse(content)
        assert "Заголовок" in result

    def test_extract_metadata(self, parser):
        """Тест извлечения метаданных."""
        content = """
        <html>
            <head>
                <title>Заголовок</title>
                <meta name="description" content="Описание">
                <meta name="keywords" content="ключевые, слова">
            </head>
            <body>
                <p>Текст</p>
            </body>
        </html>
        """
        metadata = parser.extract_metadata(content)
        assert metadata["title"] == "Заголовок"
        assert metadata["description"] == "Описание"
        assert metadata["keywords"] == "ключевые, слова"

    def test_extract_metadata_empty(self, parser):
        """Тест извлечения метаданных из пустого документа."""
        content = "<html><body><p>Текст</p></body></html>"
        metadata = parser.extract_metadata(content)
        assert metadata == {}

    def test_parse_with_scripts(self, parser):
        """Тест парсинга HTML со скриптами."""
        content = """
        <html>
        <body>
            <h1>Заголовок</h1>
            <script>
                console.log('test');
            </script>
        </body>
        </html>
        """
        result = parser.parse(content)
        assert "Заголовок" in result
        assert "console.log('test');" in result 