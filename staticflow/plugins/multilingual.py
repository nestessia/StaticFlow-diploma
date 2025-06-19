from typing import Dict, Any, Optional, List, TYPE_CHECKING
from pathlib import Path
import yaml
from .base import Plugin

if TYPE_CHECKING:
    from ..core.page import Page


class MultilingualPlugin(Plugin):
    """Плагин для поддержки многоязычности."""
    
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
        self.default_language = "en"
        self.language_config: Dict[str, Dict[str, Any]] = {}
        self.translations: Dict[str, Dict[str, str]] = {}

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

    def process_page(self, page: 'Page') -> None:
        """Обрабатывает страницу для поддержки многоязычности."""
        # Получаем язык страницы из метаданных или пути
        language = page.metadata.get(
            'language', 
            self._get_language_from_path(page.source_path)
        )
        
        # Если это страница перевода, загружаем переводы
        if language != self.default_language:
            self._load_translations(language)
            
    def _get_language_from_path(self, path: Path) -> str:
        """Определяет язык из пути файла."""
        parts = path.parts
        if len(parts) > 0 and len(parts[0]) == 2:
            return parts[0]
        return self.default_language
        
    def _load_translations(self, language: str) -> None:
        """Загружает переводы для указанного языка."""
        if language not in self.translations:
            try:
                with open(
                    f"translations/{language}.yml", 
                    'r', 
                    encoding='utf-8'
                ) as f:
                    self.translations[language] = yaml.safe_load(f)
            except FileNotFoundError:
                self.translations[language] = {}
                
    def translate(self, key: str, language: str) -> str:
        """Переводит ключ на указанный язык."""
        if language not in self.translations:
            self._load_translations(language)
            
        return self.translations[language].get(key, key)

    def get_available_translations(self, page: 'Page') -> Dict[str, Path]:
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