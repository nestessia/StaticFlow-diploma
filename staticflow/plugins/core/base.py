from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import Any, Dict, List, Optional, Set, Type
import inspect


class HookType(Enum):
    """Типы хуков для плагинов."""
    PRE_BUILD = auto()          # Перед сборкой сайта
    POST_BUILD = auto()         # После сборки сайта
    PRE_PAGE = auto()          # Перед обработкой страницы
    POST_PAGE = auto()         # После обработки страницы
    PRE_TEMPLATE = auto()      # Перед рендерингом шаблона
    POST_TEMPLATE = auto()     # После рендеринга шаблона
    PRE_ASSET = auto()         # Перед обработкой ресурса
    POST_ASSET = auto()        # После обработки ресурса


@dataclass
class PluginMetadata:
    """Метаданные плагина."""
    name: str
    version: str
    description: str
    author: str
    dependencies: List[str] = None
    requires_config: bool = False
    priority: int = 100  # Приоритет выполнения (меньше = раньше)


class Plugin(ABC):
    """Базовый класс для плагинов."""
    
    def __init__(self):
        self.config: Dict[str, Any] = {}
        self.enabled: bool = True
        self._hooks: Dict[HookType, List[str]] = {}
        
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        """Метаданные плагина."""
        pass
    
    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Инициализация плагина."""
        if config:
            self.config = config
        self._register_hooks()
    
    def _register_hooks(self) -> None:
        """Регистрирует методы-хуки на основе их имен."""
        for name, method in inspect.getmembers(self, inspect.ismethod):
            for hook_type in HookType:
                if name.lower().startswith(f"on_{hook_type.name.lower()}"):
                    if hook_type not in self._hooks:
                        self._hooks[hook_type] = []
                    self._hooks[hook_type].append(name)
    
    def has_hook(self, hook_type: HookType) -> bool:
        """Проверяет, есть ли у плагина обработчик для данного хука."""
        return hook_type in self._hooks and bool(self._hooks[hook_type])
    
    def execute_hook(self, hook_type: HookType, context: Dict[str, Any]) -> Dict[str, Any]:
        """Выполняет все обработчики для данного хука."""
        if not self.has_hook(hook_type):
            return context
            
        for method_name in self._hooks[hook_type]:
            method = getattr(self, method_name)
            try:
                context = method(context)
            except Exception as e:
                print(f"Ошибка при выполнении хука {method_name} в плагине {self.metadata.name}: {e}")
        
        return context
    
    def validate_config(self) -> bool:
        """Проверяет конфигурацию плагина."""
        return True
    
    def cleanup(self) -> None:
        """Очистка ресурсов плагина."""
        pass 