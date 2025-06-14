import pytest
from staticflow.parsers.security import ContentSecurity


class TestContentSecurity:
    """Тесты для системы безопасности контента."""

    @pytest.fixture
    def security(self):
        """Фикстура для создания системы безопасности."""

        return ContentSecurity()

    def test_sanitize_html(self, security):
        """Тест очистки HTML."""
        content = "<script>alert('test')</script><p>Текст</p>"
        result = security.sanitize_html(content)
        assert "<script>" not in result
        assert "alert('test')" not in result
        assert "Текст" in result

    def test_validate_urls(self, security):
        """Тест валидации URL."""
        assert security.is_safe_url("https://example.com") is True
        assert security.is_safe_url("http://example.com") is True
        assert security.is_safe_url("javascript:alert(1)") is False
        assert security.is_safe_url("data:text/html,<script>alert(1)</script>") is False

    def test_is_safe_url(self, security):
        """Тест проверки безопасности URL."""
        assert security.is_safe_url("https://example.com") is True
        assert security.is_safe_url("http://example.com") is True
        assert security.is_safe_url("javascript:alert(1)") is False
        assert security.is_safe_url("data:text/html,<script>alert(1)</script>") is False

    def test_sanitize_styles(self, security):
        """Тест очистки стилей."""
        content = '<div style="color: red; font-size: 12px">Текст</div>'
        result = security.sanitize_styles(content)
        assert "color: red" in result
        assert "font-size: 12px" in result

    def test_protect_against_xss(self, security):
        """Тест защиты от XSS."""
        content = '<a href="javascript:alert(1)">Click me</a>'
        result = security.protect_against_xss(content)
        assert "javascript:alert(1)" not in result
        assert "Click me" in result

    def test_security_report(self, security):
        """Тест отчета о безопасности."""
        content = """
        <script>alert('xss')</script>
        <img src="javascript:alert(1)">
        <div style="background: url(javascript:alert(1))">Текст</div>
        """
        report = security.get_security_report(content)
        assert "invalid_urls" in report
        assert "sanitized_content" in report
        assert "javascript:alert(1)" in report["invalid_urls"]
        assert "<script>" not in report["sanitized_content"]
