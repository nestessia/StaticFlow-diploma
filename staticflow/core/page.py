from pathlib import Path
from typing import Any, Dict, Optional, List
from datetime import datetime
import yaml
import os


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
        
        # Словарь переводов для страницы (URL для каждого языка)
        self.translations: Dict[str, str] = {}
        
        # Определяем язык страницы в следующем порядке:
        # 1. Явно указанный в метаданных
        # 2. По директории (если страница находится в директории языка)
        # 3. Язык по умолчанию из параметра default_lang
        self.default_lang = default_lang
        self.language = self._determine_language()
        
    def _determine_language(self) -> str:
        """Determine page language from metadata or directory."""
        # 1. Проверяем метаданные
        if "language" in self.metadata:
            return self.metadata["language"]
        
        # 2. Проверяем директорию
        if self.source_path:
            path_parts = str(self.source_path).split(os.sep)
            # Если первая часть пути выглядит как языковой код (2-3 символа)
            if path_parts and len(path_parts) > 0:
                first_dir = path_parts[0]
                if 2 <= len(first_dir) <= 3 and first_dir.islower():
                    return first_dir
        
        # 3. Возвращаем язык по умолчанию из параметра
        return self.default_lang
        
    @classmethod
    def from_file(cls, path: Path, default_lang: str = "en") -> "Page":
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
            
        page = cls(path, content, metadata, default_lang)
        
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
            
        # Получаем путь относительно корня 
        # (убираем языковой префикс если он есть)
        path_parts = list(self.source_path.parts)
        if (len(path_parts) > 1 and len(path_parts[0]) <= 3 
                and path_parts[0].islower()):
            # Если первая часть пути - языковой код, удалим его
            path_parts.pop(0)
        
        # Создаем новый путь с префиксом языка
        translation_path = Path(lang) / Path(*path_parts)
        if translation_path.exists():
            return translation_path
            
        return None
        
    def get_available_translations(self) -> List[str]:
        """Get list of available translations for this page."""
        if not self.source_path:
            return []
            
        translations = []
        
        # Получаем путь относительно корня 
        # (убираем языковой префикс если он есть)
        path_parts = list(self.source_path.parts)
        if (len(path_parts) > 1 and len(path_parts[0]) <= 3 
                and path_parts[0].islower()):
            # Если первая часть пути - языковой код, удалим его
            path_parts.pop(0)
            
        # Для каждого языкового кода проверяем, существует ли файл
        # в соответствующей директории
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
            # Если возникла ошибка при обработке пути, игнорируем
            pass
                
        return translations 