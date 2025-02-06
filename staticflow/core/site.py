from pathlib import Path
from typing import Dict, List, Optional
from .config import Config
from .page import Page


class Site:
    """Represents the entire static site."""
    
    def __init__(self, config: Config):
        self.config = config
        self.pages: Dict[str, Page] = {}
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.templates_dir: Optional[Path] = None
        
    def set_directories(self, source_dir: Path, output_dir: Path, 
                       templates_dir: Path) -> None:
        """Set the main directories for the site."""
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.templates_dir = templates_dir
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def add_page(self, page: Page) -> None:
        """Add a page to the site."""
        key = str(page.source_path.relative_to(self.source_dir))
        self.pages[key] = page
    
    def get_page(self, path: str) -> Optional[Page]:
        """Get a page by its path."""
        return self.pages.get(path)
    
    def get_all_pages(self) -> List[Page]:
        """Get all pages in the site."""
        return list(self.pages.values())
    
    def load_pages(self) -> None:
        """Load all pages from the source directory."""
        if not self.source_dir:
            raise ValueError("Source directory not set")
            
        # Clear existing pages
        self.pages.clear()
        
        # Load all markdown and HTML files
        for ext in [".md", ".html"]:
            for path in self.source_dir.rglob(f"*{ext}"):
                if path.is_file():
                    page = Page.from_file(path)
                    self.add_page(page)
    
    def get_url(self, path: str) -> str:
        """Get the full URL for a path."""
        base_url = self.config.get("base_url", "").rstrip("/")
        path = path.lstrip("/")
        return f"{base_url}/{path}" if path else base_url
    
    def clear(self) -> None:
        """Clear all pages and reset the site."""
        self.pages.clear() 