from pathlib import Path
import shutil
from .config import Config
from .site import Site
from .page import Page


class Engine:
    """Main engine for static site generation."""
    
    def __init__(self, config):
        """Initialize engine with config."""
        if isinstance(config, Config):
            self.config = config
        elif isinstance(config, (str, Path)):
            self.config = Config(config)
        else:
            raise TypeError(
                "config must be Config instance or path-like object"
            )
        self.site = Site(self.config)
        self._cache = {}
        
    def initialize(self, source_dir: Path, output_dir: Path, 
                  templates_dir: Path) -> None:
        """Initialize the engine with directory paths."""
        self.site.set_directories(source_dir, output_dir, templates_dir)
        
    def build(self) -> None:
        """Build the static site."""
        if not self.site.source_dir or not self.site.output_dir:
            raise ValueError("Source and output directories must be set")
            
        # Clear output directory
        if self.site.output_dir.exists():
            shutil.rmtree(self.site.output_dir)
        self.site.output_dir.mkdir(parents=True)
        
        # Load all pages
        self.site.load_pages()
        
        # Process pages
        self._process_pages()
        
        # Copy static assets
        self._copy_static_files()
        
    def _process_pages(self) -> None:
        """Process all pages in the site."""
        for page in self.site.get_all_pages():
            self._process_page(page)
            
    def _process_page(self, page: Page) -> None:
        """Process a single page."""
        if not self.site.source_dir or not self.site.output_dir:
            raise ValueError("Source and output directories must be set")

        # Calculate output path
        rel_path = page.source_path.relative_to(self.site.source_dir)
        output_path = (
            self.site.output_dir / rel_path.with_suffix(".html")
        )
        page.output_path = output_path

        # Create parent directories if they don't exist
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # For now, just copy the content directly to demonstrate the process
        # TODO: Add template rendering and markdown processing
        with output_path.open("w", encoding="utf-8") as f:
            # Create a simple HTML wrapper
            html = f"""<!DOCTYPE html>
<html>
<head>
    <title>{page.title}</title>
</head>
<body>
    <h1>{page.title}</h1>
    <div class="metadata">
        <p>Date: {page.metadata.get('date', '')}</p>
    </div>
    <div class="content">
        {page.content}
    </div>
</body>
</html>"""
            f.write(html)
    
    def _copy_static_files(self) -> None:
        """Copy static files to the output directory."""
        if not self.site.source_dir or not self.site.output_dir:
            return
            
        static_dir = self.site.source_dir / "static"
        if static_dir.exists():
            output_static = self.site.output_dir / "static"
            shutil.copytree(static_dir, output_static, dirs_exist_ok=True)
            
    def clean(self) -> None:
        """Clean the build artifacts."""
        if self.site.output_dir and self.site.output_dir.exists():
            shutil.rmtree(self.site.output_dir)
        self._cache.clear()
        self.site.clear()
        
    def watch(self) -> None:
        """Watch for changes and rebuild (for development)."""
        # TODO: Implement file watching logic
        pass
    
    def serve(self, host: str = "localhost", port: int = 8000) -> None:
        """Start a development server."""
        # TODO: Implement development server
        pass 