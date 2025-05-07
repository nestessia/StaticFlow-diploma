from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import yaml


class Page:
    """Represents a single page in the static site."""

    def __init__(self, source_path: Path, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.source_path = source_path
        self.content = content
        self.metadata = metadata or {}
        self.output_path: Optional[Path] = None
        self.rendered_content: Optional[str] = None
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self.language = self.metadata.get("language", "en")
        
    @classmethod
    def from_file(cls, path: Path) -> "Page":
        """Create a Page instance from a file."""
        if not path.exists():
            raise FileNotFoundError(f"Page source not found: {path}")
            
        content = ""
        metadata = {}
        
        # Read the file content
        raw_content = path.read_text(encoding="utf-8")
        
        # Parse front matter if it exists
        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    # Ensure parts[2] is a string before calling strip
                    part = parts[2]
                    if isinstance(part, Path):
                        part = str(part)
                    content = part.strip()
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid front matter in {path}: {e}")
        else:
            content = raw_content
            
        page = cls(path, content, metadata)
        
        # Update modified timestamp from file stat
        page.modified = path.stat().st_mtime
        
        return page
    
    @property
    def title(self) -> str:
        """Get the page title."""
        return self.metadata.get("title", self.source_path.stem)
    
    @property
    def url(self) -> str:
        """Get the page URL."""
        if self.output_path:
            return str(self.output_path.relative_to(self.output_path.parent.parent))
        return ""
    
    def set_output_path(self, path: Path) -> None:
        """Set the output path for the rendered page."""
        self.output_path = path
    
    def set_rendered_content(self, content: str) -> None:
        """Set the rendered content of the page."""
        self.rendered_content = content
        self.modified_at = datetime.now()
    
    def update_metadata(self, metadata: Dict[str, Any]) -> None:
        """Update page metadata."""
        self.metadata.update(metadata)
        self.modified_at = datetime.now()
        
    def get_translation_path(self, lang: str) -> Optional[Path]:
        """Get path to translation file for given language."""
        if not self.source_path:
            return None
            
        # Get the directory and filename without extension
        dir_path = self.source_path.parent
        filename = self.source_path.stem
        
        # Remove language suffix if it exists
        if "_" in filename:
            base_name = filename.rsplit("_", 1)[0]
        else:
            base_name = filename
            
        # Construct translation path
        translation_path = dir_path / f"{base_name}_{lang}{self.source_path.suffix}"
        
        return translation_path if translation_path.exists() else None
        
    def get_available_translations(self) -> List[str]:
        """Get list of available translations for this page."""
        if not self.source_path:
            return []
            
        translations = []
        dir_path = self.source_path.parent
        filename = self.source_path.stem
        
        # Remove language suffix if it exists
        if "_" in filename:
            base_name = filename.rsplit("_", 1)[0]
        else:
            base_name = filename
            
        # Look for translation files
        for file in dir_path.glob(f"{base_name}_*{self.source_path.suffix}"):
            lang = file.stem.split("_")[-1]
            if lang != self.language:
                translations.append(lang)
                
        return translations 