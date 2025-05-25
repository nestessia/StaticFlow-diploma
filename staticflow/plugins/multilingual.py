from typing import Dict, Any, Optional, List
from pathlib import Path
from .base import Plugin
from ..core.page import Page


class MultilingualPlugin(Plugin):
    """Plugin for multilingual support in StaticFlow.
    
    This plugin provides multilingual support based on directory structure:
    content/
    ├── ru/              # Russian content
    │   └── blog/
    │       └── article.md
    └── en/              # English content
        └── blog/
            └── article.md
    """

    def __init__(self):
        super().__init__()
        self.metadata = Plugin(
            name="multilingual",
            description="Directory-based multilingual support for StaticFlow",
            version="1.0.0",
            author="StaticFlow Team",
            requires_config=True
        )
        self.languages: List[str] = []
        self.default_language: str = "en"
        self.language_config: Dict[str, Dict[str, Any]] = {}

    def initialize(self, config: Optional[Dict[str, Any]] = None) -> None:
        """Initialize the plugin with configuration."""
        if not config:
            return

        # Get languages configuration
        languages_section = config.get("languages", {})
        if isinstance(languages_section, dict):
            self.languages = languages_section.get("enabled", ["en"])
            self.default_language = languages_section.get("default", "en")
            self.language_config = languages_section.get("config", {})
        else:
            self.languages = languages_section

        # Register hooks
        if hasattr(self, 'engine'):
            self.engine.hooks.register('pre_render', self.process_page)

    def get_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.languages

    def get_default_language(self) -> str:
        """Get default language."""
        return self.default_language

    def get_language_config(self, lang: str) -> Dict[str, Any]:
        """Get language-specific configuration."""
        return self.language_config.get(lang, {})

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        if not self.languages:
            return False
        if self.default_language not in self.languages:
            return False
        return True

    def process_page(self, page: Page) -> None:
        """Process page to handle multilingual content.
        
        This method:
        1. Determines the language from the directory structure
        2. Finds available translations
        3. Updates page metadata with language information
        """
        if not page.source_path:
            return

        # Determine language from directory structure
        path_parts = page.source_path.parts
        if len(path_parts) > 1:
            first_dir = path_parts[0]
            if 2 <= len(first_dir) <= 3 and first_dir.islower():
                page.language = first_dir
                page.metadata['language'] = first_dir

        # Find translations
        translations = {}
        if page.source_path.parent.parent:
            for lang in self.languages:
                if lang != page.language:
                    # Construct path to potential translation
                    rel_path = page.source_path.relative_to(
                        page.source_path.parent
                    )
                    trans_path = (
                        page.source_path.parent.parent / 
                        lang / 
                        rel_path
                    )
                    if trans_path.exists():
                        translations[lang] = trans_path

        # Update page with translation information
        page.translations = translations

    def get_available_translations(self, page: Page) -> Dict[str, Path]:
        """Get available translations for a page.
        
        Returns a dictionary mapping language codes to their file paths.
        """
        if not page.source_path:
            return {}

        translations = {}
        if page.source_path.parent.parent:
            for lang in self.languages:
                if lang != page.language:
                    rel_path = page.source_path.relative_to(
                        page.source_path.parent
                    )
                    trans_path = (
                        page.source_path.parent.parent / 
                        lang / 
                        rel_path
                    )
                    if trans_path.exists():
                        translations[lang] = trans_path

        return translations 