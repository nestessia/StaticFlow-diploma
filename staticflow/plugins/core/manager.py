from pathlib import Path
from typing import Dict, List, Optional, Type
import importlib.util
import sys
from .base import Plugin, PluginMetadata, HookType


class PluginManager:
    """Менеджер плагинов."""
    
    def __init__(self):
        self.plugins: Dict[str, Plugin] = {}
        self.plugin_configs: Dict[str, dict] = {}
        self._load_order: List[str] = []
    
    def load_plugin(self, plugin_class: Type[Plugin], config: Optional[dict] = None) -> None:
        """Загружает плагин из класса."""
        plugin = plugin_class()
        metadata = plugin.metadata
        
        # Проверяем зависимости
        if metadata.dependencies:
            for dep in metadata.dependencies:
                if dep not in self.plugins:
                    raise ValueError(
                        f"Плагин {metadata.name} требует {dep}, "
                        f"который не установлен"
                    )
        
        # Инициализируем плагин
        if config or metadata.requires_config:
            if not config:
                raise ValueError(
                    f"Плагин {metadata.name} требует конфигурацию, "
                    f"но она не предоставлена"
                )
            plugin.initialize(config)
        else:
            plugin.initialize()
            
        # Проверяем конфигурацию
        if not plugin.validate_config():
            raise ValueError(f"Неверная конфигурация для плагина {metadata.name}")
            
        self.plugins[metadata.name] = plugin
        if config:
            self.plugin_configs[metadata.name] = config
            
        # Добавляем в порядок загрузки
        self._load_order.append(metadata.name)
        self._sort_plugins()
    
    def load_plugin_from_path(self, path: Path, config: Optional[dict] = None) -> None:
        """Загружает плагин из файла."""
        if not path.exists():
            raise FileNotFoundError(f"Плагин не найден: {path}")
            
        # Загружаем модуль
        spec = importlib.util.spec_from_file_location(path.stem, path)
        if not spec or not spec.loader:
            raise ImportError(f"Не удалось загрузить плагин: {path}")
            
        module = importlib.util.module_from_spec(spec)
        sys.modules[path.stem] = module
        spec.loader.exec_module(module)
        
        # Ищем класс плагина
        plugin_class = None
        for item in dir(module):
            obj = getattr(module, item)
            if (isinstance(obj, type) and 
                issubclass(obj, Plugin) and 
                obj != Plugin):
                plugin_class = obj
                break
                
        if not plugin_class:
            raise ValueError(f"Класс плагина не найден в {path}")
            
        self.load_plugin(plugin_class, config)
    
    def _sort_plugins(self) -> None:
        """Сортирует плагины по приоритету и зависимостям."""
        def get_priority(name: str) -> int:
            return self.plugins[name].metadata.priority
            
        self._load_order.sort(key=get_priority)
    
    def execute_hook(self, hook_type: HookType, context: Dict[str, any]) -> Dict[str, any]:
        """Выполняет хук для всех плагинов."""
        for name in self._load_order:
            plugin = self.plugins[name]
            if plugin.enabled and plugin.has_hook(hook_type):
                context = plugin.execute_hook(hook_type, context)
        return context
    
    def get_plugin(self, name: str) -> Optional[Plugin]:
        """Получает плагин по имени."""
        return self.plugins.get(name)
    
    def disable_plugin(self, name: str) -> None:
        """Отключает плагин."""
        if plugin := self.plugins.get(name):
            plugin.enabled = False
    
    def enable_plugin(self, name: str) -> None:
        """Включает плагин."""
        if plugin := self.plugins.get(name):
            plugin.enabled = True
    
    def cleanup(self) -> None:
        """Очищает все плагины."""
        for plugin in self.plugins.values():
            try:
                plugin.cleanup()
            except Exception as e:
                print(f"Ошибка при очистке плагина {plugin.metadata.name}: {e}")
        self.plugins.clear()
        self.plugin_configs.clear()
        self._load_order.clear() 