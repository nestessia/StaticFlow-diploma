from typing import Dict, List, Any, Optional
from pathlib import Path

class ParserManager:
    def __init__(self):
        self.parsers: Dict[str, 'Parser'] = {}

    def add_parser(self, extension: str, parser: 'Parser') -> None:
        self.parsers[extension] = parser

    def get_parser(self, extension: str) -> 'Parser':
        return self.parsers.get(extension)

    def determine_parser_by_extension(self, extension: str) -> 'Parser':
        return self.get_parser(extension)

    def print_parser_not_found_error(self, extension: str) -> None:
        print(f"Парсер для расширения {extension} не найден")

class Engine:
    def __init__(self, config: 'Configuration'):
        self.configuration = config
        self.site: Optional['Site'] = None
        self._cache: Dict[str, Any] = {}
        self.parser_manager = ParserManager()
        self.plugins: List['Plugin'] = []

    def add_plugin(self, plugin: 'Plugin') -> None:
        self.plugins.append(plugin)

    def add_parser(self, extension: str, parser: 'Parser') -> None:
        self.parser_manager.add_parser(extension, parser)

    def initialize(self, source_dir: Path, output_dir: Path, templates_dir: Path) -> None:
        self.site = Site(self.configuration)
        self.site.set_folders(source_dir, output_dir, templates_dir)

    def build(self) -> None:
        if not self.site:
            raise ValueError("Сайт не инициализирован")
        self._process_pages()
        self._copy_static_files()

    def _process_pages(self) -> None:
        for page in self.site.get_all_pages():
            self._process_page(page)

    def _process_page(self, page: 'Page') -> None:
        # Обработка страницы
        pass

    def _copy_static_files(self) -> None:
        # Копирование статических файлов
        pass

    def clear(self) -> None:
        self._cache.clear()
        for plugin in self.plugins:
            plugin.clear()

class Site:
    def __init__(self, config: 'Configuration'):
        self.configuration = config
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.templates_dir: Optional[Path] = None
        self.pages: List['Page'] = []

    def set_folders(self, source_dir: Path, output_dir: Path, templates_dir: Path) -> None:
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.templates_dir = templates_dir

    def load_pages(self) -> None:
        # Загрузка страниц
        pass

    def get_all_pages(self) -> List['Page']:
        return self.pages

    def clear(self) -> None:
        self.pages.clear()

class Configuration:
    def __init__(self, config_path: Path):
        self.settings: Dict[str, Any] = {}
        self.config_path = config_path

    def load(self) -> None:
        # Загрузка конфигурации
        pass

    def get(self, key: str) -> Any:
        return self.settings.get(key)

    def set(self, key: str, value: Any) -> None:
        self.settings[key] = value

class Cache:
    def __init__(self, lifetime: int = 3600, max_size: int = 1000):
        self._cache: Dict[str, Any] = {}
        self._lifetime = lifetime
        self._max_size = max_size

    def get(self, key: str) -> Any:
        return self._cache.get(key)

    def set(self, key: str, value: Any, lifetime: Optional[int] = None) -> None:
        self._cache[key] = value

    def delete(self, key: str) -> None:
        if key in self._cache:
            del self._cache[key]

    def clear(self) -> None:
        self._cache.clear()

    def check_expiration(self, key: str) -> bool:
        # Проверка срока действия
        return True

    def get_statistics(self) -> Dict[str, Any]:
        return {
            "size": len(self._cache),
            "max_size": self._max_size,
            "lifetime": self._lifetime
        } 