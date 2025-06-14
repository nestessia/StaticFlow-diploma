import pytest
import logging
from staticflow.utils.logging import get_logger, setup_logging
from staticflow.utils.pygments_utils import generate_pygments_css


class TestLogging:
    """Тесты для модуля логирования."""

    def test_setup_logging(self, tmp_path):
        """Тест настройки логирования."""
        log_file = tmp_path / "test.log"
        setup_logging(level="info", log_file=str(log_file))
        logger = get_logger("test")
        logger.info("Test message")
        assert log_file.exists()
        assert "Test message" in log_file.read_text()


class TestPygmentsUtils:
    """Тесты для утилит Pygments."""

    def test_generate_pygments_css(self):
        """Тест генерации CSS стилей."""
        css = generate_pygments_css()
        assert ".highlight" in css
        assert "background-color" in css

    def test_generate_pygments_css_with_custom_style(self):
        """Тест генерации CSS стилей с пользовательским стилем."""
        css = generate_pygments_css(style_name="monokai")
        assert ".highlight" in css
        assert "background-color" in css
