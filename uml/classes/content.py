from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime


class Page:
    def __init__(self, source_path: Path):
        self.source_path = source_path
        self.output_path: Optional[Path] = None
        self.content: str = ""
        self.metadata: Dict[str, Any] = {}
        self.title: str = ""
        self.format: str = ""
        self.history = ChangeHistory(self)
        self.cache: Optional['Cache'] = None

    def render(self, template: str) -> None:
        # Рендеринг страницы
        pass

    def load(self) -> None:
        # Загрузка содержимого
        pass

    def get_format(self) -> str:
        return self.format

    def get_cached_content(self) -> str:
        if self.cache:
            return self.cache.get(str(self.source_path)) or ""
        return ""

    def save_to_cache(self, content: str, lifetime: int) -> None:
        if self.cache:
            self.cache.set(str(self.source_path), content, lifetime)

    def add_to_history(self, content: str, author: str) -> None:
        self.history.add_version(content, author)

    def rollback_to_version(self, version_id: str) -> None:
        version = self.history.get_version(version_id)
        if version:
            self.content = version.content


class ChangeHistory:
    def __init__(self, page: 'Page'):
        self.page = page
        self.versions: List['Version'] = []

    def add_version(self, content: str, author: str) -> None:
        version = Version(content, author)
        self.versions.append(version)

    def get_version(self, version_id: str) -> Optional['Version']:
        for version in self.versions:
            if version.id == version_id:
                return version
        return None

    def get_all_versions(self) -> List['Version']:
        return self.versions


class Version:
    def __init__(self, content: str, author: str):
        self.id = str(datetime.now().timestamp())
        self.date = datetime.now()
        self.author = author
        self.content = content

    def compare_with(self, version: 'Version') -> Dict[str, Any]:
        # Сравнение версий
        return {
            "same_content": self.content == version.content,
            "same_author": self.author == version.author,
            "time_diff": (self.date - version.date).total_seconds()
        } 