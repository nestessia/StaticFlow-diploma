import pytest
from pathlib import Path
import tempfile
import toml
from staticflow.core.config import Config


class TestConfig:
    """Тесты для класса конфигурации."""

    @pytest.fixture
    def config(self):
        """Фикстура для создания конфигурации."""
        return Config()

    @pytest.fixture
    def temp_config_file(self):
        """Фикстура для создания временного конфигурационного файла."""
        with tempfile.NamedTemporaryFile(suffix=".toml", delete=False, mode='w', encoding='utf-8') as f:
            config_data = {
                "site_name": "Test Site",
                "base_url": "https://example.com",
                "languages": ["en", "ru"],
                "default_language": "en",
                "language_config": {
                    "en": {"name": "English"},
                    "ru": {"name": "Русский"}
                }
            }
            toml.dump(config_data, f)
            return Path(f.name)

    def test_init_default(self, config):
        """Тест инициализации с значениями по умолчанию."""
        assert config.get("languages") == ["en"]
        assert config.get("default_language") == "en"
        assert config.get("environment") == "development"

    def test_load_config(self, temp_config_file):
        """Тест загрузки конфигурации из файла."""
        config = Config(temp_config_file)
        assert config.get("site_name") == "Test Site"
        assert config.get("base_url") == "https://example.com"
        assert config.get("languages") == ["en", "ru"]

    def test_load_nonexistent_file(self):
        """Тест загрузки несуществующего файла."""
        with pytest.raises(FileNotFoundError):
            Config(Path("nonexistent.toml"))

    def test_get_set(self, config):
        """Тест получения и установки значений."""
        config.set("test_key", "test_value")
        assert config.get("test_key") == "test_value"
        assert config.get("nonexistent", "default") == "default"

    def test_save_config(self, config, temp_config_file):
        """Тест сохранения конфигурации в файл."""
        config.set("site_name", "New Site")
        config.save(temp_config_file)
        
        new_config = Config(temp_config_file)
        assert new_config.get("site_name") == "New Site"

    def test_get_languages(self, config):
        """Тест получения списка языков."""
        assert config.get_languages() == ["en"]
        config.set("languages", ["en", "ru"])
        assert config.get_languages() == ["en", "ru"]

    def test_get_default_language(self, config):
        """Тест получения языка по умолчанию."""
        assert config.get_default_language() == "en"
        config.set("default_language", "ru")
        assert config.get_default_language() == "ru"

    def test_get_language_config(self, config):
        """Тест получения конфигурации языка."""
        config.set("language_config", {
            "en": {"name": "English"},
            "ru": {"name": "Русский"}
        })
        assert config.get_language_config("en") == {"name": "English"}
        assert config.get_language_config("ru") == {"name": "Русский"}
        assert config.get_language_config("fr") == {}

    def test_validate_config(self, config):
        """Тест валидации конфигурации."""
        with pytest.raises(ValueError) as exc_info:
            config._validate_config()
        assert "Missing required config fields" in str(exc_info.value)

        config.set("site_name", "Test Site")
        config.set("base_url", "https://example.com")
        config._validate_config()  # Не должно вызывать исключение

    def test_environment(self, config):
        """Тест работы с окружением."""
        assert config.environment == "development"
        config.set_environment("production")
        assert config.environment == "production"

    def test_config_path(self, config):
        """Тест работы с путем к конфигурационному файлу."""
        assert config.config_path is None
        config.set("_config_path", Path("/test/path/config.toml"))
        assert str(config.config_path).replace("\\", "/") == "/test/path/config.toml" 