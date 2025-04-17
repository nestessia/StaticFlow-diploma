from pathlib import Path
from typing import Any, Dict, Optional
import re
from datetime import datetime


class Router:
    """URL router for StaticFlow."""
    
    DEFAULT_ROUTES = {
        "page": "{slug}/index.html",
        "post": "posts/{year}/{month}/{slug}/index.html",
        "tag": "tags/{slug}/index.html",
        "category": "categories/{slug}/index.html",
        "author": "authors/{slug}/index.html",
        "index": "index.html",
        "archive": "archive/index.html"
    }
    
    def __init__(self, config_routes: Optional[Dict[str, str]] = None):
        """Initialize router with optional routes from config."""
        self.routes = self.DEFAULT_ROUTES.copy()
        
        # Update routes from config if provided
        if config_routes:
            self.routes.update(config_routes)
    
    def get_route_pattern(self, content_type: str) -> str:
        """Get the route pattern for a content type."""
        default_pattern = self.routes.get("page", "{slug}/index.html")
        return self.routes.get(content_type, default_pattern)
    
    def generate_url(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Generate a URL for a content item based on the router config."""
        if content_type not in self.routes:
            return ""

        pattern = self.routes.get(content_type, "")
        # Ensure pattern is a string
        pattern = str(pattern)
        
        url = pattern
        if not url:
            return ""

        # Replace placeholders with metadata values
        def replace_placeholder(match):
            key = match.group(1)
            
            # Special handling for date components
            if key == "year" and "date" in metadata:
                return self._format_date(metadata["date"], "%Y")
            elif key == "month" and "date" in metadata:
                return self._format_date(metadata["date"], "%m")
            elif key == "day" and "date" in metadata:
                return self._format_date(metadata["date"], "%d")
            
            # Regular metadata lookup
            return str(metadata.get(key, ""))
        
        url = re.sub(r'\{([^}]+)\}', replace_placeholder, url)
        
        # Ensure no double slashes (except in protocol)
        url = re.sub(r"(?<!:)//+", "/", url)
        
        return url
    
    def get_output_path(
        self, base_dir: Path, content_type: str, metadata: Dict[str, Any]
    ) -> Path:
        """Get the full output path for a content item."""
        url = self.generate_url(content_type, metadata)
        # Ensure base_dir is a Path object
        if not isinstance(base_dir, Path):
            base_dir = Path(str(base_dir))
        # Ensure url is a string
        url = str(url)
        return base_dir / url
    
    def _format_date(self, date_value: Any, format_str: str) -> str:
        """Format a date value according to the given format."""
        if isinstance(date_value, datetime):
            return date_value.strftime(format_str)
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value)
                return date_obj.strftime(format_str)
            except (ValueError, TypeError):
                return ""
        return "" 