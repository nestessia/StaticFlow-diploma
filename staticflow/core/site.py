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
        
        # Инициализируем маршрутизатор с настройками из конфига
        router_config = config.get('router', {})
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
                if filename.endswith(('.md', '.html', '.txt')):
                    file_path = Path(root) / filename
                    files.append(file_path)
        return files
        
    def _load_page(self, file_path: Path) -> None:
        """Load a single page from file."""
        if not self.source_dir:
            raise ValueError("Source directory not set")
            
        rel_path = file_path.relative_to(self.source_dir)
        page = Page.from_file(file_path)
        
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
            parent_dir = page.source_path.parent.name
            # Если родительский каталог не пустой и не точка,
            # используем его как категорию
            if parent_dir and parent_dir != '.':
                metadata["category"] = parent_dir
        
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