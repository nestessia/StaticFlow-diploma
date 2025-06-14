import pytest
from typing import Dict, Any, Optional
from staticflow.plugins.core.base import Plugin, PluginMetadata, HookType
from staticflow.plugins.core.manager import PluginManager


class TestPlugin(Plugin):
    """Тестовый плагин для проверки базовой функциональности."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="test_plugin",
            version="1.0.0",
            description="Test plugin",
            author="Test Author",
            requires_config=True
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().initialize(config)
        self.initialized = True
        self.config = config or {}
    
    def process_content(self, content: str) -> str:
        return f"Processed: {content}"
    
    def validate_config(self) -> bool:
        return "test_key" in self.config
    
    def cleanup(self) -> None:
        self.initialized = False


class DependentPlugin(Plugin):
    """Тестовый плагин с зависимостями."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="dependent_plugin",
            version="1.0.0",
            description="Plugin with dependencies",
            author="Test Author",
            dependencies=["test_plugin"]
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().initialize(config)
        self.initialized = True


class HookPlugin(Plugin):
    """Тестовый плагин с хуками."""
    
    def __init__(self):
        super().__init__()
        self.hook_called = False
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="hook_plugin",
            version="1.0.0",
            description="Plugin with hooks",
            author="Test Author"
        )
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        super().initialize(config)
        self.hook_called = False
    
    def on_pre_template(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.hook_called = True
        context["processed"] = True
        return context


@pytest.fixture
def plugin_manager():
    return PluginManager()


@pytest.fixture
def test_plugin():
    return TestPlugin()


@pytest.fixture
def dependent_plugin():
    return DependentPlugin()


@pytest.fixture
def hook_plugin():
    return HookPlugin()


def test_plugin_initialization(test_plugin):
    """Тест инициализации плагина."""
    config = {"test_key": "test_value"}
    test_plugin.initialize(config)
    assert test_plugin.initialized
    assert test_plugin.config == config


def test_plugin_content_processing(test_plugin):
    """Тест обработки контента плагином."""
    content = "test content"
    processed = test_plugin.process_content(content)
    assert processed == f"Processed: {content}"


def test_plugin_config_validation(test_plugin):
    """Тест валидации конфигурации плагина."""
    # Невалидная конфигурация
    test_plugin.initialize({"invalid_key": "value"})
    assert not test_plugin.validate_config()
    
    # Валидная конфигурация
    test_plugin.initialize({"test_key": "value"})
    assert test_plugin.validate_config()


def test_plugin_cleanup(test_plugin):
    """Тест очистки ресурсов плагина."""
    test_plugin.initialize()
    assert test_plugin.initialized
    test_plugin.cleanup()
    assert not test_plugin.initialized


def test_plugin_manager_load_plugin(plugin_manager, test_plugin):
    """Тест загрузки плагина в менеджер."""
    config = {"test_key": "test_value"}
    plugin_manager.load_plugin(test_plugin.__class__, config)
    assert "test_plugin" in plugin_manager.plugins
    assert plugin_manager.plugins["test_plugin"].config == config


def test_plugin_manager_dependencies(
    plugin_manager, test_plugin, dependent_plugin
):
    """Тест загрузки плагина с зависимостями."""
    # Сначала загружаем зависимый плагин
    with pytest.raises(ValueError):
        plugin_manager.load_plugin(dependent_plugin.__class__)
    
    # Загружаем основной плагин
    plugin_manager.load_plugin(test_plugin.__class__, {"test_key": "value"})
    
    # Теперь можно загрузить зависимый плагин
    plugin_manager.load_plugin(dependent_plugin.__class__)
    assert "dependent_plugin" in plugin_manager.plugins


def test_plugin_manager_enable_disable(plugin_manager, test_plugin):
    """Тест включения/отключения плагина."""
    plugin_manager.load_plugin(test_plugin.__class__, {"test_key": "value"})
    assert plugin_manager.plugins["test_plugin"].enabled
    
    plugin_manager.disable_plugin("test_plugin")
    assert not plugin_manager.plugins["test_plugin"].enabled
    
    plugin_manager.enable_plugin("test_plugin")
    assert plugin_manager.plugins["test_plugin"].enabled


def test_plugin_manager_cleanup(plugin_manager, test_plugin):
    """Тест очистки менеджера плагинов."""
    plugin_manager.load_plugin(test_plugin.__class__, {"test_key": "value"})
    assert len(plugin_manager.plugins) > 0
    
    plugin_manager.cleanup()
    assert len(plugin_manager.plugins) == 0
    assert len(plugin_manager.plugin_configs) == 0
    assert len(plugin_manager._load_order) == 0 