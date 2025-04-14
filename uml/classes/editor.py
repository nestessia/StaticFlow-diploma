from typing import Optional


class Editor:
    def __init__(self, page: 'Page', cache: 'Cache'):
        self.page = page
        self.cache = cache

    def save_changes(self, content: str) -> None:
        self.page.content = content
        self.page.add_to_history(content, "editor")

    def get_preview(self) -> str:
        return self.page.get_cached_content()

    def get_change_history(self) -> list:
        return self.page.history.get_all_versions()

    def rollback_changes(self, version_id: str) -> None:
        self.page.rollback_to_version(version_id)

    def get_cached_preview(self) -> str:
        return self.cache.get(f"preview_{self.page.source_path}") or ""

    def save_preview_to_cache(self, content: str) -> None:
        self.cache.set(f"preview_{self.page.source_path}", content) 