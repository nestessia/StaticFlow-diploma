import pytest
from click.testing import CliRunner
from pathlib import Path
import threading
import time
import requests
import shutil
from staticflow.cli.build import build
from staticflow.cli.serve import serve
from staticflow.cli.create import create
from staticflow.core.engine import Engine


@pytest.fixture
def runner():
    """Фикстура для создания CLI runner."""
    return CliRunner()


@pytest.fixture
def config_file(tmp_path):
    """Фикстура для создания временного конфигурационного файла."""
    # Создаем необходимые директории
    content_dir = tmp_path / "content"
    templates_dir = tmp_path / "templates"
    static_dir = tmp_path / "static"
    output_dir = tmp_path / "output"

    content_dir.mkdir()
    templates_dir.mkdir()
    static_dir.mkdir()
    output_dir.mkdir()

    # Создаем тестовый шаблон
    template_file = templates_dir / "default.html"
    template_content = """
<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
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
    page_file = content_dir / "index.md"
    page_content = """---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
"""
    page_file.write_text(page_content)

    # Создаем конфигурационный файл
    config_content = """
site_name = "Test Site"
base_url = "http://example.com"
default_language = "en"
USE_LANGUAGE_PREFIXES = true
EXCLUDE_DEFAULT_LANG_PREFIX = true
CLEAN_URLS = true
PRESERVE_DIRECTORY_STRUCTURE = true
template_dir = "templates"
source_dir = "content"
output_dir = "output"
static_dir = "static"
"""
    config_path = tmp_path / "config.toml"
    config_path.write_text(config_content)
    return config_path


@pytest.fixture
def test_dirs(tmp_path):
    """Фикстура для создания тестовых директорий."""
    source_dir = tmp_path / "content"
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

    return {
        "source_dir": source_dir,
        "output_dir": output_dir,
        "templates_dir": templates_dir,
        "static_dir": static_dir
    }


class TestBuildCommand:
    """Тесты для команды build."""

    def test_build_with_valid_config(self, runner, config_file):
        """Тест сборки с валидной конфигурацией."""
        with runner.isolated_filesystem():
            # Копируем все необходимые файлы и директории
            config_path = Path("config.toml")
            config_path.write_text(config_file.read_text())
            
            content_dir = Path("content")
            content_dir.mkdir()
            (content_dir / "index.md").write_text("""---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
""")
            
            templates_dir = Path("templates")
            templates_dir.mkdir()
            (templates_dir / "default.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>""")
            
            static_dir = Path("static")
            static_dir.mkdir()
            
            output_dir = Path("output")
            output_dir.mkdir()
            
            result = runner.invoke(build, ['--config', 'config.toml'])
            assert result.exit_code == 0
            assert "Error" not in result.output

    def test_build_with_invalid_config(self, runner, tmp_path):
        """Тест сборки с невалидной конфигурацией."""
        result = runner.invoke(build, ['--config', 'invalid.toml'])
        assert result.exit_code == 0  # Click возвращает 0 даже при ошибке
        assert "Config file not found" in result.output

    def test_build_with_custom_config_path(self, runner, config_file):
        """Тест сборки с пользовательским путем к конфигурации."""
        with runner.isolated_filesystem():
            # Копируем все необходимые файлы и директории
            config_path = Path("custom_config.toml")
            config_path.write_text(config_file.read_text())
            
            content_dir = Path("content")
            content_dir.mkdir()
            (content_dir / "index.md").write_text("""---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
""")
            
            templates_dir = Path("templates")
            templates_dir.mkdir()
            (templates_dir / "default.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>""")
            
            static_dir = Path("static")
            static_dir.mkdir()
            
            output_dir = Path("output")
            output_dir.mkdir()
            
            result = runner.invoke(build, ['-c', 'custom_config.toml'])
            assert result.exit_code == 0
            assert "Error" not in result.output


class TestServeCommand:
    """Тесты для команды serve."""

    def test_serve_with_valid_config(self, runner, config_file):
        """Тест запуска сервера с валидной конфигурацией."""
        with runner.isolated_filesystem():
            # Копируем все необходимые файлы и директории
            config_path = Path("config.toml")
            config_path.write_text(config_file.read_text())
            
            content_dir = Path("content")
            content_dir.mkdir()
            (content_dir / "index.md").write_text("""---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
""")
            
            templates_dir = Path("templates")
            templates_dir.mkdir()
            (templates_dir / "default.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>""")
            
            static_dir = Path("static")
            static_dir.mkdir()
            
            output_dir = Path("output")
            output_dir.mkdir()

            # Сначала собираем сайт
            engine = Engine(config_path)
            engine.initialize(content_dir, output_dir, templates_dir)
            engine.build()

            # Запускаем сервер в отдельном потоке
            def run_server():
                runner.invoke(serve, [
                    '--config', 'config.toml',
                    '--port', '8000',
                    '--host', 'localhost'
                ])

            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()

            # Даем серверу время на запуск
            time.sleep(2)

            try:
                # Проверяем, что сервер отвечает
                response = requests.get('http://localhost:8000')
                assert response.status_code == 200
            finally:
                # Останавливаем сервер
                requests.get('http://localhost:8000/shutdown')

    def test_serve_with_invalid_config(self, runner, tmp_path):
        """Тест запуска сервера с невалидной конфигурацией."""
        result = runner.invoke(serve, [
            '--config', 'invalid.toml',
            '--port', '8000',
            '--host', 'localhost'
        ])
        assert result.exit_code == 0  # Click возвращает 0 даже при ошибке
        assert "Config file not found" in result.output

    def test_serve_with_custom_port(self, runner, config_file):
        """Тест запуска сервера с пользовательским портом."""
        with runner.isolated_filesystem():
            # Копируем все необходимые файлы и директории
            config_path = Path("config.toml")
            config_path.write_text(config_file.read_text())
            
            content_dir = Path("content")
            content_dir.mkdir()
            (content_dir / "index.md").write_text("""---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
""")
            
            templates_dir = Path("templates")
            templates_dir.mkdir()
            (templates_dir / "default.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>""")
            
            static_dir = Path("static")
            static_dir.mkdir()
            
            output_dir = Path("output")
            output_dir.mkdir()

            # Сначала собираем сайт
            engine = Engine(config_path)
            engine.initialize(content_dir, output_dir, templates_dir)
            engine.build()

            # Запускаем сервер в отдельном потоке
            def run_server():
                runner.invoke(serve, [
                    '--config', 'config.toml',
                    '--port', '8080',
                    '--host', 'localhost'
                ])

            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()

            # Даем серверу время на запуск
            time.sleep(2)

            try:
                # Проверяем, что сервер отвечает
                response = requests.get('http://localhost:8080')
                assert response.status_code == 200
            finally:
                # Останавливаем сервер
                requests.get('http://localhost:8080/shutdown')

    def test_serve_with_custom_host(self, runner, config_file):
        """Тест запуска сервера с пользовательским хостом."""
        with runner.isolated_filesystem():
            # Копируем все необходимые файлы и директории
            config_path = Path("config.toml")
            config_path.write_text(config_file.read_text())
            
            content_dir = Path("content")
            content_dir.mkdir()
            (content_dir / "index.md").write_text("""---
title: Test Page
date: 2024-03-20
template: default.html
---

# Test Content
This is a test page content.
""")
            
            templates_dir = Path("templates")
            templates_dir.mkdir()
            (templates_dir / "default.html").write_text("""<!DOCTYPE html>
<html>
<head>
    <title>{{ page.title }}</title>
</head>
<body>
    <h1>{{ page.title }}</h1>
    <div class="content">
        {{ page_content }}
    </div>
</body>
</html>""")
            
            static_dir = Path("static")
            static_dir.mkdir()
            
            output_dir = Path("output")
            output_dir.mkdir()

            # Сначала собираем сайт
            engine = Engine(config_path)
            engine.initialize(content_dir, output_dir, templates_dir)
            engine.build()

            # Запускаем сервер в отдельном потоке
            def run_server():
                runner.invoke(serve, [
                    '--config', 'config.toml',
                    '--port', '8000',
                    '--host', '127.0.0.1'
                ])

            server_thread = threading.Thread(target=run_server)
            server_thread.daemon = True
            server_thread.start()

            # Даем серверу время на запуск
            time.sleep(2)

            try:
                # Проверяем, что сервер отвечает
                response = requests.get('http://127.0.0.1:8000')
                assert response.status_code == 200
            finally:
                # Останавливаем сервер
                requests.get('http://127.0.0.1:8000/shutdown')


class TestCreateCommand:
    """Тесты для команды create."""

    def test_create_with_existing_directory(self, runner, tmp_path):
        """Тест создания проекта в существующей директории."""
        project_dir = tmp_path / "test_project"
        project_dir.mkdir()
        result = runner.invoke(create, [str(project_dir)])
        assert result.exit_code == 0
        assert "already exists" in result.output

    def test_create_with_invalid_path(self, runner):
        """Тест создания проекта с невалидным путем."""
        result = runner.invoke(create, ["/invalid/path"])
        assert result.exit_code == 0
        assert "Error" in result.output

    def test_create_with_multilingual(self, runner, tmp_path):
        """Тест создания многоязычного проекта."""
        with runner.isolated_filesystem():
            project_dir = Path("multilingual_project")
            result = runner.invoke(
                create,
                [str(project_dir)],
                input="Test Site\nTest Description\nTest Author\nen\ny\nfr\ndone\n"
            )
            assert result.exit_code == 0
            assert project_dir.exists()
            
            # Проверяем создание языковых директорий
            content_dir = project_dir / "content"
            assert content_dir.exists()
            assert (content_dir / "en").exists()
            assert (content_dir / "fr").exists() 