from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class Plugin(ABC):
    """Base class for all StaticFlow plugins."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.engine = None
    
    @abstractmethod
    def process_content(self, content: str) -> str:
        """Process the content and return modified version."""
        pass
    
    def initialize(self) -> None:
        """Initialize the plugin. Called when plugin is loaded."""
        pass
    
    def cleanup(self) -> None:
        """Cleanup resources. Called when site generation is complete."""
        pass 