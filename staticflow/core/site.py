from pathlib import Path
from typing import Dict, List, Optional
from .config import Config
from .page import Page
from .router import Router


class Site:
    """Represents the entire static site."""
    
    def __init__(self, config: Config):
        self.config = config
        self.pages: Dict[str, Page] = {}
        self.source_dir: Optional[Path] = None
        self.output_dir: Optional[Path] = None
        self.templates_dir: Optional[Path] = None
        
        # Initialize router with routes from config
        config_routes = config.get("routes", {})
        self.router = Router(config_routes)
        
    def set_directories(
        self, source_dir: Path, output_dir: Path, templates_dir: Path
    ) -> None:
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
    
    def generate_page_output_path(self, page: Page) -> Path:
        """Generate the output path for a page using the router."""
        if not self.output_dir:
            raise ValueError("Output directory not set")
            
        # Build metadata for URL generation
        metadata = page.metadata.copy()
        
        # Ensure slug is available
        if "slug" not in metadata:
            metadata["slug"] = page.source_path.stem
            
        # Determine content type
        content_type = self.determine_content_type(page)
        
        # Use router to generate output path
        output_path = self.router.get_output_path(
            self.output_dir, content_type, metadata
        )
        
        # Create parent directories
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        return output_path
    
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
                    
                    # Set the output path using the router
                    output_path = self.generate_page_output_path(page)
                    page.set_output_path(output_path)
                    
                    self.add_page(page)
    
    def get_url(self, path: str) -> str:
        """Get the full URL for a path."""
        base_url = self.config.get("base_url", "").rstrip("/")
        path = path.lstrip("/")
        return f"{base_url}/{path}" if path else base_url
    
    def clear(self) -> None:
        """Clear all pages and reset the site."""
        self.pages.clear() 