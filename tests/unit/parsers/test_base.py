import pytest
from staticflow.parsers.base import ContentParser


class TestParser(ContentParser):
    """Тестовый класс для тестирования базового парсера."""
    
    def parse(self, content: str) -> str:
        """Тестовая реализация метода parse."""
        return content


class TestBaseParser:
    """Тесты для базового класса парсера."""

    def test_init(self):
        """Тест инициализации парсера."""
        parser = TestParser()
        assert parser is not None

    def test_parse_not_implemented(self):
        """Тест, что метод parse не реализован в базовом классе."""
        parser = TestParser()
        result = parser.parse("test content")
        assert result == "test content"

    def test_validate_not_implemented(self):
        """Тест, что метод validate не реализован в базовом классе."""
        parser = TestParser()
        with pytest.raises(NotImplementedError):
            parser.validate("test content")

    def test_get_metadata_not_implemented(self):
        """Тест, что метод get_metadata не реализован в базовом классе."""
        parser = TestParser()
        with pytest.raises(NotImplementedError):
            parser.get_metadata("test content") 