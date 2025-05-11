from pathlib import Path
import os
from typing import Dict, List, Optional
from .config import Config
from .page import Page
from .router import Router
from ..plugins import initialize_plugins


class Site:
    """Site representation for StaticFlow."""
    
    def __init__(self, config: Config):
        """Initialize Site with Config."""
        self.config = config
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.template_dir: Optional[Path] = None
        self.pages: Dict[str, Page] = {}
        self.languages = config.get_languages()
        self.default_language = config.get_default_language()
        
        # Инициализируем маршрутизатор с настройками из конфига
        router_config = config.get('router', {})
        
        # Добавляем информацию о языках в настройки маршрутизатора
        if 'default_language' not in router_config:
            router_config['default_language'] = self.default_language
            
        # Флаг использования языковых префиксов
        if 'USE_LANGUAGE_PREFIXES' not in router_config:
            router_config['USE_LANGUAGE_PREFIXES'] = config.get(
                'USE_LANGUAGE_PREFIXES', True)
            
        # Флаг исключения префикса для языка по умолчанию
        if 'EXCLUDE_DEFAULT_LANG_PREFIX' not in router_config:
            router_config['EXCLUDE_DEFAULT_LANG_PREFIX'] = config.get(
                'EXCLUDE_DEFAULT_LANG_PREFIX', True)
            
        self.router = Router(router_config)
        
    def set_directories(
        self,
        source_dir: Path,
        output_dir: Path,
        template_dir: Path
    ) -> None:
        """Set directory paths for the site."""
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.template_dir = template_dir
        
    def load_pages(self) -> None:
        """Load all content pages from source directory."""
        if not self.source_dir:
            raise ValueError("Source directory not set")
            
        self.pages.clear()
        
        for file_path in self._get_content_files():
            self._load_page(file_path)
            
    def _get_content_files(self) -> List[Path]:
        """Get all content files from source directory."""
        if not self.source_dir:
            return []
            
        files = []
        for root, _, filenames in os.walk(self.source_dir):
            for filename in filenames:
                if filename.endswith(('.md', '.html', '.txt', '.rst')):
                    file_path = Path(root) / filename
                    files.append(file_path)
        return files
        
    def _load_page(self, file_path: Path) -> None:
        """Load a single page from file."""
        if not self.source_dir:
            raise ValueError("Source directory not set")
            
        rel_path = file_path.relative_to(self.source_dir)
        # Передаем язык по умолчанию из конфига при создании страницы
        page = Page.from_file(file_path, default_lang=self.default_language)
        
        # Если язык не указан явно, используем язык из конфига
        if "language" not in page.metadata:
            # Проверяем, находится ли файл в языковой директории
            if len(rel_path.parts) > 0:
                first_dir = rel_path.parts[0]
                if (2 <= len(first_dir) <= 3 and 
                        first_dir.islower() and 
                        first_dir in self.languages):
                    page.language = first_dir
                else:
                    # Используем язык по умолчанию из конфигурации
                    page.language = self.default_language
            else:
                page.language = self.default_language
                
            # Обновляем метаданные страницы
            page.metadata["language"] = page.language
        
        # Сохраняем относительный путь для дальнейшего использования
        page.source_path = rel_path
        
        # Generate output path using router
        if self.output_dir:
            output_path = self.generate_page_output_path(page)
            page.set_output_path(output_path)
            
        self.pages[str(rel_path)] = page
        
    def generate_page_output_path(self, page: Page) -> Path:
        """Generate output path for a page using router."""
        if not self.output_dir:
            raise ValueError("Output directory not set")
        
        # Определение типа контента
        content_type = self.determine_content_type(page)
        
        # Подготовка метаданных для маршрутизатора
        metadata = page.metadata.copy()
        
        # Ensure slug is available
        if "slug" not in metadata:
            metadata["slug"] = page.source_path.stem
            
        # Extract category from path if not specified
        if "category" not in metadata and "/" in str(page.source_path):
            path_parts = str(page.source_path).split('/')
            
            # Пропускаем первую часть пути, если она похожа на языковой код
            if len(path_parts) > 1 and path_parts[0] in self.languages:
                parent_dir = path_parts[1] if len(path_parts) > 2 else ""
            else:
                parent_dir = path_parts[0]
                
            # Если родительский каталог не пустой и не точка,
            # используем его как категорию
            if parent_dir and parent_dir != '.':
                metadata["category"] = parent_dir
                
        # Add language to metadata
        metadata["language"] = page.language
        
        # Generate the full output path using the router
        return self.router.get_output_path(
            self.output_dir, 
            content_type, 
            metadata
        )
        
    def get_page(self, rel_path: str) -> Optional[Page]:
        """Get a page by relative path."""
        return self.pages.get(rel_path)
        
    def get_all_pages(self) -> List[Page]:
        """Get all pages."""
        return list(self.pages.values())
        
    def get_pages_by_language(self, lang: str) -> List[Page]:
        """Get all pages for a specific language."""
        return [p for p in self.pages.values() if p.language == lang]
        
    def get_page_translations(self, page: Page) -> Dict[str, Page]:
        """Get all translations of a page."""
        translations = {}
        for lang in page.get_available_translations():
            trans_path = page.get_translation_path(lang)
            if trans_path and self.source_dir:
                # Проверяем, существует ли перевод в списке страниц
                try:
                    rel_path = trans_path.relative_to(self.source_dir)
                    trans_page = self.pages.get(str(rel_path))
                    if trans_page:
                        translations[lang] = trans_page
                except ValueError:
                    # Файл вне source_dir
                    pass
        return translations
        
    def get_page_translation_urls(self, page: Page) -> Dict[str, str]:
        """Get URLs of all translations for a page."""
        translation_urls = {}
        translations = self.get_page_translations(page)
        
        for lang, trans_page in translations.items():
            if trans_page.output_path and self.output_dir:
                try:
                    # Получаем URL перевода относительно корня сайта
                    url = "/" + str(
                        trans_page.output_path.relative_to(self.output_dir)
                    )
                    translation_urls[lang] = url
                except ValueError:
                    # Не удалось получить относительный путь
                    pass
                
        return translation_urls
        
    def clear(self) -> None:
        """Clear all loaded pages."""
        self.pages.clear()
        
    def initialize_plugins(self, engine) -> None:
        """Initialize all plugins for the engine."""
        initialize_plugins(engine)
    
    def determine_content_type(self, page: Page) -> str:
        """Determine the content type of a page."""
        # First check if the content type is specified in the metadata
        if "type" in page.metadata:
            return page.metadata["type"]
        
        # Check if it's in a special directory
        source_path_str = str(page.source_path)
        if "/posts/" in source_path_str or "\\posts\\" in source_path_str:
            return "post"
        
        # Check if it's an index file
        if page.source_path.stem == "index":
            return "index"
            
        # Default to page
        return "page"
    
    def get_url(self, path: str) -> str:
        """Get the full URL for a path."""
        # Get the full URL for a path.
        base_url = self.config.get("base_url", "")
        
        # Преобразуем Path в строку, если нужно
        if isinstance(base_url, Path):
            base_url = str(base_url)
            
        base_url = base_url.rstrip("/")
        # Ensure path is a string before calling lstrip
        if isinstance(path, Path):
            path = str(path)
        path = path.lstrip("/")
        return f"{base_url}/{path}" if path else base_url 