from pathlib import Path
from typing import Any, Dict
import re
from datetime import datetime
from .category import CategoryManager, Category


class Router:
    """Router for StaticFlow."""

    DEFAULT_URL_PATTERNS = {
        "page": "{category}/{slug}",         
        "post": "{category_path}/{slug}",
        "tag": "{name}",
        "category": "{category_path}",
        "author": "{name}",
        "index": "",
    }

    DEFAULT_SAVE_AS_PATTERNS = {
        "page": "{category}/{slug}/index.html",
        "post": "{category_path}/{slug}/index.html",
        "tag": "{name}/index.html",
        "category": "{category_path}/index.html",
        "author": "{name}/index.html",
        "index": "index.html",
    }

    def __init__(self, config: Dict[str, Any]):
        """Initialize router with config."""
        self.url_patterns = config.get(
            "URL_PATTERNS", 
            self.DEFAULT_URL_PATTERNS
        )
        self.save_as_patterns = config.get(
            "SAVE_AS_PATTERNS", 
            self.DEFAULT_SAVE_AS_PATTERNS
        )
        self.use_clean_urls = True
        self.use_language_prefixes = config.get(
            "USE_LANGUAGE_PREFIXES", True
        )
        self.exclude_default_lang_prefix = config.get(
            "EXCLUDE_DEFAULT_LANG_PREFIX", 
            True
        )
        self.default_language = config.get("default_language", "en")
        self.default_page = config.get("router", {}).get("DEFAULT_PAGE", "index")
        self.category_manager = CategoryManager()
        self._url_cache: Dict[str, str] = {}
        self._save_as_cache: Dict[str, str] = {}
        self.preserve_directory_structure = True

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
        self.preserve_directory_structure = config.get(
            'PRESERVE_DIRECTORY_STRUCTURE', True
        )

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

        if (content_type == 'page' and
                metadata.get('slug') == self.default_page):
            return '/'

        pattern = self.url_patterns.get(content_type)
        if not pattern:
            if 'slug' in metadata:
                return f"/{metadata['slug']}"
            return "/"

        if self.preserve_directory_structure and 'source_path' in metadata:
            source_path = Path(metadata['source_path'])
            if source_path.parent.name != 'content':
                directory = str(source_path.parent.relative_to(
                    source_path.parents[len(source_path.parts)-2]
                )).replace('\\', '/')
                metadata['directory'] = directory

        if 'category' in metadata:
            category_path = self._get_category_path(metadata['category'])
            metadata['category_path'] = category_path

        url = self._format_pattern(pattern, metadata)

        if self.use_clean_urls and url.endswith('.html'):
            url = url[:-5]

        if 'language' in metadata and hasattr(self, 'engine'):
            multilingual_plugin = self.engine.get_plugin('multilingual')
            if multilingual_plugin:
                url = multilingual_plugin.get_language_url(
                    url, metadata['language']
                )

        if not url.startswith('/'):
            url = '/' + url

        self._url_cache[cache_key] = url
        return url

    def get_save_as(self, content_type: str, metadata: Dict[str, Any]) -> str:
        """Get save path for content."""
        cache_key = f"{content_type}:{hash(str(metadata))}"
        if cache_key in self._save_as_cache:
            return self._save_as_cache[cache_key]

        if 'save_as' in metadata:
            return metadata['save_as']

        if (content_type == 'page' and 
                metadata.get('slug') == self.default_page):
            return 'index.html'

        pattern = self.save_as_patterns.get(content_type)
        if not pattern:
            return self.get_url(content_type, metadata)

        if self.preserve_directory_structure and 'source_path' in metadata:
            source_path = Path(metadata['source_path'])
            if source_path.parent.name != 'content':
                directory = str(source_path.parent.relative_to(
                    source_path.parents[len(source_path.parts)-2]
                )).replace('\\', '/')
                metadata['directory'] = directory

        if 'category' in metadata:
            category_path = self._get_category_path(metadata['category'])
            metadata['category_path'] = category_path

        save_as = self._format_pattern(pattern, metadata)

        if 'language' in metadata and hasattr(self, 'engine'):
            multilingual_plugin = self.engine.get_plugin('multilingual')
            if multilingual_plugin:
                save_as = multilingual_plugin.get_language_save_path(
                    save_as, metadata['language']
                )

        self._save_as_cache[cache_key] = save_as
        return save_as

    def get_output_path(
        self,
        output_dir: Path,
        content_type: str,
        metadata: Dict[str, Any]
    ) -> Path:
        """Get output path for content."""
        if content_type == "page":
            category = metadata.get("category")
            if not category:
                pattern = "{slug}.html"
            else:
                pattern = self.save_as_patterns.get(
                    content_type, "{category}/{slug}/index.html"
                )
        else:
            pattern = self.save_as_patterns.get(content_type, "{slug}.html")

        variables = metadata.copy()

        if content_type == "category" and "category_path" in metadata:
            variables["category"] = metadata["category_path"]
            variables["category_path"] = metadata["category_path"]
        elif content_type == "post" and "category" in metadata:
            variables["category_path"] = metadata["category"]
        elif "source_path" in metadata:
            source_path = Path(metadata["source_path"])
            if source_path.parent.name != "content":
                directory = str(source_path.parent).replace("\\", "/")
                if directory.startswith("content/"):
                    directory = directory[8:]
                variables["directory"] = directory
                variables["category"] = directory
                variables["category_path"] = directory

        try:
            save_as_path = pattern.format(**variables)
        except KeyError as e:
            print(f"Warning: Missing key in pattern: {e}")
            save_as_path = f"{variables.get('slug', 'index')}.html"
        save_as_path = save_as_path.lstrip("/").replace("\\", "/")

        output_path = output_dir / save_as_path
        return output_path

    def _get_category_path(self, category: Any) -> str:
        """Get full category path from category object or string."""
        print(f"\nProcessing category: {category}")
        if isinstance(category, Category):
            result = category.full_path
        elif isinstance(category, list) and category:
            cat = self.category_manager.get_or_create_category(category[0])
            result = cat.full_path
        else:
            cat = self.category_manager.get_or_create_category(str(category))
            result = cat.full_path
        print(f"Resulting category path: {result}")
        return result

    def _format_pattern(self, pattern: str, metadata: Dict[str, Any]) -> str:
        """Replace all variables in pattern with values from metadata."""
        result = pattern

        for match in re.finditer(r'\{([^}]+)\}', pattern):
            key = match.group(1)

            if key == 'directory' and 'directory' in metadata:
                replacement = metadata['directory']
            elif key == 'category_path' and 'category_path' in metadata:
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
