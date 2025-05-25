from typing import Dict, Any, Optional, List
from .base import Plugin


class MultilingualPlugin(Plugin):
    """Plugin for multilingual support in StaticFlow."""

    def __init__(self):
        super().__init__()
        self.metadata = Plugin(
            name="multilingual",
            description="Multilingual support for StaticFlow",
            version="1.0.0",
            author="StaticFlow Team",
            requires_config=True
        )
        self.languages: List[str] = []
        self.default_language: str = "en"
        self.use_language_prefixes: bool = True
        self.exclude_default_lang_prefix: bool = True
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
            self.use_language_prefixes = languages_section.get(
                "USE_LANGUAGE_PREFIXES", True
            )
            self.exclude_default_lang_prefix = languages_section.get(
                "EXCLUDE_DEFAULT_LANG_PREFIX", True
            )
            self.language_config = languages_section.get("config", {})
        else:
            self.languages = languages_section

    def get_languages(self) -> List[str]:
        """Get list of supported languages."""
        return self.languages

    def get_default_language(self) -> str:
        """Get default language."""
        return self.default_language

    def get_language_config(self, lang: str) -> Dict[str, Any]:
        """Get language-specific configuration."""
        return self.language_config.get(lang, {})

    def should_use_language_prefix(self, language: str) -> bool:
        """Check if language prefix should be used for URL."""
        if not self.use_language_prefixes:
            return False
        if (language == self.default_language and 
                self.exclude_default_lang_prefix):
            return False
        return True

    def get_language_url(self, url: str, language: str) -> str:
        """Get URL with language prefix if needed."""
        if not self.should_use_language_prefix(language):
            return url

        if url == "index.html" or url == "index":
            return f"{language}/"
        return f"{language}/{url}"

    def get_language_save_path(self, save_path: str, language: str) -> str:
        """Get save path with language prefix if needed."""
        if not self.should_use_language_prefix(language):
            return save_path

        if save_path == "index.html":
            return f"{language}/index.html"
        return f"{language}/{save_path}"

    def validate_config(self) -> bool:
        """Validate plugin configuration."""
        if not self.languages:
            return False
        if self.default_language not in self.languages:
            return False
        return True 