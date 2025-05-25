from pathlib import Path
from typing import Any, Dict, Optional
import re
from datetime import datetime
import os
from .category import CategoryManager, Category


class Router:
    """URL router for StaticFlow."""

    DEFAULT_URL_PATTERNS = {
        "page": "{slug}.html",                           
        "post": "{category_path}/{slug}.html",
        "tag": "tag/{name}.html",
        "category": "category/{category_path}/index.html",
        "author": "author/{name}.html",
        "index": "index.html",
        "archive": "archives.html"
    }

    DEFAULT_SAVE_AS_PATTERNS = {
        "page": "{slug}.html",  
        "post": "{category_path}/{slug}.html",
        "tag": "tag/{name}.html",
        "category": "category/{category_path}/index.html",
        "author": "author/{name}.html",
        "index": "index.html",
        "archive": "archives.html"
    }

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize router with optional routes from config."""
        self.url_patterns = self.DEFAULT_URL_PATTERNS.copy()
        self.save_as_patterns = self.DEFAULT_SAVE_AS_PATTERNS.copy()
        self.use_clean_urls = False
        self.use_language_prefixes = False
        self.exclude_default_lang_prefix = True
        self.default_language = 'ru'
        self.default_page = 'index'
        self.category_manager = CategoryManager()
        self._url_cache: Dict[str, str] = {}
        self._save_as_cache: Dict[str, str] = {}

        if config:
            self.update_config(config)
    
    def update_config(self, config: Dict[str, Any]) -> None:
        """Update router configuration from site config."""
        url_patterns = config.get('URL_PATTERNS', {})
        if url_patterns:
            self.url_patterns.update(url_patterns)

        save_as_patterns = config.get('SAVE_AS_PATTERNS', {})
        if save_as_patterns:
            self.save_as_patterns.update(save_as_patterns)

        self.use_clean_urls = config.get('CLEAN_URLS', False)
        self.use_language_prefixes = config.get('USE_LANGUAGE_PREFIXES', True)
        self.exclude_default_lang_prefix = config.get(
            'EXCLUDE_DEFAULT_LANG_PREFIX', True
        )
        self.default_language = config.get('default_language', 'ru')
        self.default_page = config.get('DEFAULT_PAGE', 'index')

        # Load categories if provided
        categories_file = config.get('CATEGORIES_FILE')
        if categories_file:
            self.category_manager = CategoryManager.load_from_file(
                Path(categories_file)
            )

    def get_url(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Get URL for content based on type and metadata."""
        cache_key = f"{content_type}:{hash(str(metadata))}"
        if cache_key in self._url_cache:
            return self._url_cache[cache_key]

        if 'url' in metadata:
            return metadata['url']

        # Если это дефолтная страница и запрос к корню сайта
        if (content_type == 'page' and 
                metadata.get('slug') == self.default_page):
            return ''

        pattern = self.url_patterns.get(content_type)
        if not pattern:
            if 'slug' in metadata:
                return f"{metadata['slug']}.html"
            return ""

        # Handle category paths
        if 'category' in metadata:
            category_path = self._get_category_path(metadata['category'])
            metadata['category_path'] = category_path

        url = self._format_pattern(pattern, metadata)

        if self.use_clean_urls and url.endswith('.html'):
            url = url[:-5]

        if self.use_language_prefixes and 'language' in metadata:
            language = metadata['language']
            if (language != self.default_language or 
                    not self.exclude_default_lang_prefix):
                if url == "index.html" or (self.use_clean_urls and url == "index"):
                    if self.use_clean_urls:
                        url = f"{language}/"
                    else:
                        url = f"{language}/index.html"
                else:
                    url = f"{language}/{url}"

        self._url_cache[cache_key] = url
        return url

    def get_save_as(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Get save path for content."""
        cache_key = f"{content_type}:{hash(str(metadata))}"
        if cache_key in self._save_as_cache:
            return self._save_as_cache[cache_key]

        if 'save_as' in metadata:
            return metadata['save_as']

        # Если это дефолтная страница
        if (content_type == 'page' and 
                metadata.get('slug') == self.default_page):
            return 'index.html'

        pattern = self.save_as_patterns.get(content_type)
        if not pattern:
            return self.get_url(content_type, metadata)

        # Handle category paths
        if 'category' in metadata:
            category_path = self._get_category_path(metadata['category'])
            metadata['category_path'] = category_path

        save_as = self._format_pattern(pattern, metadata)

        if self.use_language_prefixes and 'language' in metadata:
            language = metadata['language']
            if (language != self.default_language or 
                    not self.exclude_default_lang_prefix):
                if save_as == "index.html":
                    save_as = f"{language}/index.html"
                else:
                    save_as = f"{language}/{save_as}"

        self._save_as_cache[cache_key] = save_as
        return save_as

    def get_output_path(
        self, base_dir: Path, content_type: str, metadata: Dict[str, Any]
    ) -> Path:
        """Get full output path for file."""
        save_as = self.get_save_as(content_type, metadata)

        if os.path.isabs(save_as):
            return Path(save_as)

        return base_dir / save_as

    def _get_category_path(self, category: Any) -> str:
        """Get full category path from category object or string."""
        if isinstance(category, Category):
            return category.full_path
        elif isinstance(category, list) and category:
            # Handle list of categories, use first one
            cat = self.category_manager.get_or_create_category(category[0])
            return cat.full_path
        else:
            # Handle string category
            cat = self.category_manager.get_or_create_category(str(category))
            return cat.full_path

    def _format_pattern(self, pattern: str, metadata: Dict[str, Any]) -> str:
        """Replace all variables in pattern with values from metadata."""
        result = pattern

        for match in re.finditer(r'\{([^}]+)\}', pattern):
            key = match.group(1)

            if key == 'category_path' and 'category_path' in metadata:
                replacement = metadata['category_path']
            elif key == 'category' and 'category' in metadata:
                category = metadata['category']
                if isinstance(category, list) and category:
                    replacement = category[0]
                else:
                    replacement = str(category)
            elif key in ('year', 'month', 'day') and 'date' in metadata:
                if key == 'year':
                    replacement = self._format_date(metadata['date'], '%Y')
                elif key == 'month':
                    replacement = self._format_date(metadata['date'], '%m')
                elif key == 'day':
                    replacement = self._format_date(metadata['date'], '%d')
                else:
                    replacement = ''
            else:
                replacement = str(metadata.get(key, ''))

            pattern_to_replace = '{' + key + '}'
            result = result.replace(pattern_to_replace, replacement)

        return self._normalize_path(result)

    def _normalize_path(self, path: str) -> str:
        """Normalize path (remove double slashes etc)."""
        normalized = re.sub(r'(?<!:)//+', '/', path)
        if normalized.endswith('/') and len(normalized) > 1:
            normalized = normalized[:-1]
        return normalized

    def _format_date(self, date_value: Any, format_str: str) -> str:
        """Format date value according to format string."""
        if isinstance(date_value, datetime):
            return date_value.strftime(format_str)
        elif isinstance(date_value, str):
            try:
                date_obj = datetime.fromisoformat(date_value)
                return date_obj.strftime(format_str)
            except (ValueError, TypeError):
                return ""
        return ""

    def clear_cache(self) -> None:
        """Clear URL and save_as caches."""
        self._url_cache.clear()
        self._save_as_cache.clear()
