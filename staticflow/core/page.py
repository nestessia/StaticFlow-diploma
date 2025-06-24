from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import yaml
import os
import jinja2


class Page:
    """Represents a single page in the static site."""

    def __init__(self, source_path: Path, content: str, 
                 metadata: Optional[Dict[str, Any]] = None,
                 default_lang: str = "en"):
        self.source_path = source_path
        self.content = content
        self.metadata = metadata or {}
        self.output_path: Optional[Path] = None
        self.rendered_content: Optional[str] = None
        self.created_at = datetime.now()
        self.modified_at = datetime.now()
        self._markdown_parser = None

        self.translations: Dict[str, str] = {}
        self.default_lang = default_lang
        self.language = self._determine_language()

    @property
    def markdown_parser(self):
        if self._markdown_parser is None:
            from staticflow.parsers import MarkdownParser
            self._markdown_parser = MarkdownParser()
        return self._markdown_parser

    def _determine_language(self) -> str:
        """Determine page language from metadata or directory."""
        if "language" in self.metadata:
            return self.metadata["language"]

        if self.source_path:
            path_parts = str(self.source_path).split(os.sep)
            if path_parts and len(path_parts) > 0:
                first_dir = path_parts[0]
                if 2 <= len(first_dir) <= 3 and first_dir.islower():
                    return first_dir

        return self.default_lang

    @classmethod
    def from_file(cls, path: Path, default_lang: str = "en") -> "Page":
        """Create a Page instance from a file."""
        if not path.exists():
            raise FileNotFoundError(f"Page source not found: {path}")

        content = ""
        metadata = {}

        raw_content = path.read_text(encoding="utf-8")

        if raw_content.startswith("---"):
            parts = raw_content.split("---", 2)
            if len(parts) >= 3:
                try:
                    metadata = yaml.safe_load(parts[1])
                    part = parts[2]
                    if isinstance(part, Path):
                        part = str(part)
                    content = part.strip()
                except yaml.YAMLError as e:
                    raise ValueError(f"Invalid front matter in {path}: {e}")
        else:
            content = raw_content

        page = cls(path, content, metadata, default_lang)
        page.modified = path.stat().st_mtime
        return page

    @property
    def title(self) -> str:
        """Get the page title."""
        return self.metadata.get("title", self.source_path.stem)

    @property
    def date(self) -> Optional[datetime]:
        """Get the page date."""
        if "date" in self.metadata:
            date_value = self.metadata["date"]
            if isinstance(date_value, str):
                try:
                    return datetime.fromisoformat(date_value)
                except ValueError:
                    return None
            return date_value
        return None

    @property
    def url(self) -> str:
        """Get the page URL."""
        if self.output_path:
            return str(self.output_path.relative_to(
                self.output_path.parent.parent))
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

        path_parts = list(self.source_path.parts)
        if (len(path_parts) > 1 and len(path_parts[0]) <= 3 
                and path_parts[0].islower()):
            path_parts.pop(0)

        translation_path = Path(lang) / Path(*path_parts)
        if translation_path.exists():
            return translation_path

        return None

    def get_available_translations(self) -> List[str]:
        """Get list of available translations for this page."""
        if not self.source_path:
            return []

        translations = []

        path_parts = list(self.source_path.parts)
        if (len(path_parts) > 1 and len(path_parts[0]) <= 3
                and path_parts[0].islower()):
            path_parts.pop(0)

        try:
            parent_dir = self.source_path.parent.parent
            lang_dirs = [
                d for d in parent_dir.iterdir() 
                if d.is_dir() and len(d.name) <= 3 and d.name.islower()
            ]

            for lang_dir in lang_dirs:
                lang = lang_dir.name
                if lang != self.language:
                    translation_path = lang_dir / Path(*path_parts)
                    if translation_path.exists():
                        translations.append(lang)
        except Exception:
            pass

        return translations

    def render(self) -> str:
        """Render the page to HTML."""
        if self.rendered_content:
            return self.rendered_content

        html_content = self.markdown_parser.parse(self.content)

        template_name = self.metadata.get('template')
        if template_name:
            try:
                template_dir = Path('templates')
                env = jinja2.Environment(
                    loader=jinja2.FileSystemLoader(str(template_dir))
                )
                template = env.get_template(template_name)

                context = {
                    'content': html_content,
                    'page': self,
                    'metadata': self.metadata
                }

                self.rendered_content = template.render(**context)
            except Exception as e:
                print(f"Error rendering template {template_name}: {e}")
                self.rendered_content = html_content
        else:
            self.rendered_content = html_content

        return self.rendered_content

    @property
    def author(self) -> Optional[str]:
        """Get the page author from metadata."""
        return self.metadata.get("author")

    @property
    def category(self) -> Optional[str]:
        """Get the page category from metadata."""
        return self.metadata.get("category")

    @property
    def tags(self) -> List[str]:
        """Get the page tags from metadata."""
        tags = self.metadata.get("tags", [])
        if isinstance(tags, str):
            return [tag.strip() for tag in tags.split(",")]
        return tags if isinstance(tags, list) else []

    @property
    def template(self) -> str:
        """Get the page template from metadata or default."""
        return self.metadata.get("template", "page.html")
