from typing import Dict, List, Optional, Any
from pathlib import Path
import yaml


class Category:
    """Represents a category in the site hierarchy."""

    def __init__(self, name: str, parent: Optional['Category'] = None):
        self.name = name
        self.parent = parent
        self.children: List[Category] = []
        self.posts: List[Any] = []
        self.metadata: Dict[str, Any] = {}
        self.slug = self._generate_slug(name)

    def _generate_slug(self, name: str) -> str:
        """Generate URL-friendly slug from category name."""
        return name.lower().replace(' ', '-')

    @property
    def full_path(self) -> str:
        """Get full category path including parents."""
        if self.parent:
            return f"{self.parent.full_path}/{self.slug}"
        return self.slug

    @property
    def level(self) -> int:
        """Get category level in hierarchy (0 for root categories)."""
        if self.parent:
            return self.parent.level + 1
        return 0

    def add_child(self, category: 'Category') -> None:
        """Add child category."""
        category.parent = self
        self.children.append(category)

    def add_post(self, post: Any) -> None:
        """Add post to category."""
        self.posts.append(post)

    def get_all_posts(self) -> List[Any]:
        """Get all posts in category and its subcategories."""
        posts = self.posts.copy()
        for child in self.children:
            posts.extend(child.get_all_posts())
        return posts

    def to_dict(self) -> Dict[str, Any]:
        """Convert category to dictionary representation."""
        return {
            'name': self.name,
            'slug': self.slug,
            'full_path': self.full_path,
            'level': self.level,
            'metadata': self.metadata,
            'children': [child.to_dict() for child in self.children],
            'post_count': len(self.posts)
        }


class CategoryManager:
    """Manages categories and their hierarchy."""

    def __init__(self):
        self.categories: Dict[str, Category] = {}
        self.root_categories: List[Category] = []

    def get_or_create_category(self, path: str) -> Category:
        """Get existing category or create new one from path."""
        if path in self.categories:
            return self.categories[path]

        parts = path.split('/')
        current_path = ""
        parent = None
        category = None

        for part in parts:
            if current_path:
                current_path += "/"
            current_path += part

            if current_path in self.categories:
                parent = self.categories[current_path]
                continue

            category = Category(part, parent)
            self.categories[current_path] = category

            if parent:
                parent.add_child(category)
            else:
                self.root_categories.append(category)

            parent = category

        return category

    def get_category(self, path: str) -> Optional[Category]:
        """Get category by path."""
        return self.categories.get(path)

    def get_all_categories(self) -> List[Category]:
        """Get all categories as flat list."""
        return list(self.categories.values())

    def get_root_categories(self) -> List[Category]:
        """Get root level categories."""
        return self.root_categories

    def to_dict(self) -> Dict[str, Any]:
        """Convert category manager to dictionary representation."""
        return {
            'categories': {
                path: cat.to_dict() for path, cat in self.categories.items()
            },
            'root_categories': [cat.to_dict() for cat in self.root_categories]
        }

    def save_to_file(self, path: Path) -> None:
        """Save category structure to YAML file."""
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(self.to_dict(), f, allow_unicode=True)

    @classmethod
    def load_from_file(cls, path: Path) -> 'CategoryManager':
        """Load category structure from YAML file."""
        manager = cls()
        if not path.exists():
            return manager

        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)

        for path, cat_data in data.get('categories', {}).items():
            category = manager.get_or_create_category(path)
            category.metadata = cat_data.get('metadata', {})

        return manager 