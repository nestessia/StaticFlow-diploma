import pytest
import os
import tempfile
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Создает временную директорию для тестов."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield Path(tmp_dir)

@pytest.fixture
def sample_project(temp_dir):
    """Создает структуру тестового проекта."""
    project_dir = temp_dir / "sample_project"
    project_dir.mkdir()
    
    # Создаем базовую структуру проекта
    (project_dir / "content").mkdir()
    (project_dir / "templates").mkdir()
    (project_dir / "static").mkdir()
    
    # Создаем тестовый контент
    with open(project_dir / "content" / "index.md", "w", encoding="utf-8") as f:
        f.write("# Test Page\n\nThis is a test page.")
    
    return project_dir 