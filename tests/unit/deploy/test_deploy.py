import pytest
from pathlib import Path
from staticflow.deploy.github_pages import GitHubPagesDeployer
from staticflow.core.config import Config


@pytest.fixture
def config(tmp_path):
    """Создает временную конфигурацию для тестов."""
    config = Config()
    config.set('source_dir', str(tmp_path / "source"))
    config.set('output_dir', str(tmp_path / "output"))
    config.set('build_dir', str(tmp_path / "build"))
    config.set('deploy', {
        "type": "github_pages",
        "repo": "test/repo",
        "branch": "gh-pages",
        "token": "test_token"
    })
    return config


class TestGitHubPagesDeployer:
    """Тесты для деплоя на GitHub Pages."""

    def test_init(self, config, tmp_path):
        """Тест инициализации деплоера."""
        site_path = tmp_path / "output"
        site_path.mkdir(parents=True)
        deployer = GitHubPagesDeployer(str(site_path))
        assert deployer.site_path == site_path

    def test_validate_config(self, config, tmp_path):
        """Тест валидации конфигурации."""
        site_path = tmp_path / "output"
        site_path.mkdir(parents=True)
        deployer = GitHubPagesDeployer(str(site_path))
        deployer.update_config(
            repo_url="https://github.com/test/repo",
            username="test",
            email="test@example.com"
        )
        is_valid, errors, warnings = deployer.validate_config()
        assert is_valid
        assert not errors
        assert not warnings

    def test_prepare_deployment(self, config, tmp_path):
        """Тест подготовки к деплою."""
        site_path = tmp_path / "output"
        site_path.mkdir(parents=True)
        deployer = GitHubPagesDeployer(str(site_path))
        deployer.update_config(
            repo_url="https://github.com/test/repo",
            username="test",
            email="test@example.com"
        )
        is_valid, errors, warnings = deployer.validate_config()
        assert is_valid
        assert not errors
        assert not warnings