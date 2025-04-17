from typing import Dict, Any, Optional
from abc import ABC, abstractmethod


class Parser(ABC):
    def __init__(self, engine: 'Engine'):
        self.engine = engine

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def parse(self, content: str) -> Dict[str, Any]:
        pass

    @abstractmethod
    def convert(self, content: str) -> str:
        pass

    @abstractmethod
    def get_metadata(self) -> Dict[str, Any]:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass


class Plugin(ABC):
    def __init__(self, engine: 'Engine'):
        self.engine = engine

    @abstractmethod
    def initialize(self) -> None:
        pass

    @abstractmethod
    def process_page(self, page: 'Page') -> None:
        pass

    @abstractmethod
    def process_site(self, site: 'Site') -> None:
        pass

    @abstractmethod
    def process_content(self, content: str) -> str:
        pass

    @abstractmethod
    def get_title(self) -> str:
        pass

    @abstractmethod
    def clear(self) -> None:
        pass

    def get_cached_result(self, key: str) -> Optional[Any]:
        if hasattr(self, 'cache'):
            return self.cache.get(key)
        return None

    def save_to_cache(self, key: str, value: Any, lifetime: int) -> None:
        if hasattr(self, 'cache'):
            self.cache.set(key, value, lifetime) 