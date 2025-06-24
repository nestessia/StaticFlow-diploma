import pytest
from staticflow.parsers.validation import ContentValidator


class TestContentValidator:
    """Тесты для валидатора контента."""

    @pytest.fixture
    def validator(self):
        """Фикстура для создания валидатора."""
        return ContentValidator()

    def test_validate_structure(self, validator):
        """Тест валидации структуры HTML."""
        content = "<div><p>Текст</p></div>"
        assert validator.validate_structure(content) is True

    def test_validate_structure_invalid(self, validator):
        """Тест валидации некорректной структуры HTML."""
        content = "<div><p>Незакрытый тег"
        assert validator.validate_structure(content) is False

    def test_validate_attributes(self, validator):
        """Тест валидации атрибутов."""
        content = '<a href="https://example.com">Ссылка</a>'
        assert validator.validate_attributes(content) is True

    def test_validate_nesting(self, validator):
        """Тест валидации вложенности тегов."""
        content = "<div><p>Текст</p></div>"
        assert validator.validate_nesting(content) is True

    def test_validate_nesting_invalid(self, validator):
        """Тест валидации некорректной вложенности тегов."""
        content = "<p><div>Некорректная вложенность</p></div>"
        validator.validate_nesting(content)
        assert len(validator.errors) > 0
        assert any("вложенность" in error.lower() for error in validator.errors)

    def test_strict_validation(self, validator):
        """Тест строгой валидации."""
        validator.strict = True
        content = "<div><p>Текст</p></div>"
        assert validator.validate_structure(content) is True
        assert validator.validate_attributes(content) is True
        assert validator.validate_nesting(content) is True

    def test_relaxed_validation(self, validator):
        """Тест нестрогой валидации."""
        validator.strict = False
        content = "<div><p>Текст</p></div>"
        assert validator.validate_structure(content) is True
        assert validator.validate_attributes(content) is True
        assert validator.validate_nesting(content) is True