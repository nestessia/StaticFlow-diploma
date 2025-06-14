import pytest
from pathlib import Path
from staticflow.templates.engine import TemplateEngine
from staticflow.templates.loader import load_template_file, load_default_template


@pytest.fixture
def template_dir(tmp_path):
    """Создает временную директорию с тестовыми шаблонами."""
    template_dir = tmp_path / "templates"
    template_dir.mkdir()
    
    # Создаем базовый шаблон
    base_template = template_dir / "base.html"
    base_template.write_text("""
    <!DOCTYPE html>
    <html>
    <head>
        <title>{{ title }}</title>
    </head>
    <body>
        {% block content %}{% endblock %}
    </body>
    </html>
    """)
    
    # Создаем шаблон страницы
    page_template = template_dir / "page.html"
    page_template.write_text("""
    {% extends "base.html" %}
    {% block content %}
    <h1>{{ title }}</h1>
    <div>{{ content }}</div>
    {% endblock %}
    """)
    
    return template_dir


class TestTemplateEngine:
    """Тесты для движка шаблонов."""
    
    def test_init(self, template_dir):
        """Тест инициализации движка шаблонов."""
        engine = TemplateEngine(str(template_dir))
        assert engine.templates_dir == str(template_dir)
    
    def test_get_template(self, template_dir):
        """Тест получения шаблона."""
        engine = TemplateEngine(str(template_dir))
        template = engine.get_template("page.html")
        assert template is not None
        result = template.render(title="Test Page", content="Test Content")
        assert "Test Page" in result
        assert "Test Content" in result
    
    def test_get_template_missing(self, template_dir):
        """Тест получения отсутствующего шаблона."""
        engine = TemplateEngine(str(template_dir))
        with pytest.raises(Exception):
            engine.get_template("missing.html")
    
    def test_get_template_invalid(self, template_dir):
        """Тест получения невалидного шаблона."""
        invalid_template = template_dir / "invalid.html"
        invalid_template.write_text("{% invalid syntax %}")
        
        engine = TemplateEngine(str(template_dir))
        with pytest.raises(Exception):
            engine.get_template("invalid.html")


class TestTemplateLoader:
    """Тесты для загрузчика шаблонов."""
    
    def test_load_template_file(self, template_dir):
        """Тест загрузки файла шаблона."""
        template_path = template_dir / "base.html"
        content = load_template_file(str(template_path))
        assert "{% block content %}" in content
    
    def test_load_template_file_missing(self):
        """Тест загрузки отсутствующего файла шаблона."""
        with pytest.raises(FileNotFoundError):
            load_template_file("missing.html")
    
    def test_load_default_template(self):
        """Тест загрузки шаблона по умолчанию."""
        with pytest.raises(FileNotFoundError):
            load_default_template("missing.html") 