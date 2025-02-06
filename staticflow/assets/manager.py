from pathlib import Path
from typing import Dict, List, Optional, Set
import shutil
from PIL import Image
import hashlib


class AssetManager:
    """Менеджер статических ресурсов."""
    
    def __init__(self, source_dir: Path, output_dir: Path):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.processed_files: Set[Path] = set()
        self.image_sizes = {
            'thumbnail': (150, 150),
            'small': (300, 300),
            'medium': (800, 800),
            'large': (1200, 1200)
        }
    
    def process_assets(self) -> None:
        """Обрабатывает все статические ресурсы."""
        if not self.source_dir.exists():
            return
            
        # Создаем выходную директорию
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Обрабатываем изображения
        self._process_images()
        
        # Копируем остальные файлы
        self._copy_other_files()
    
    def _process_images(self) -> None:
        """Обрабатывает изображения с оптимизацией."""
        image_exts = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and file_path.suffix.lower() in image_exts:
                self._optimize_image(file_path)
                self.processed_files.add(file_path)
    
    def _optimize_image(self, image_path: Path) -> None:
        """Оптимизирует изображение и создает разные размеры."""
        try:
            with Image.open(image_path) as img:
                # Создаем директорию для разных размеров
                output_dir = self.output_dir / image_path.parent.relative_to(self.source_dir)
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Сохраняем оригинал
                output_path = output_dir / image_path.name
                img.save(output_path, optimize=True, quality=85)
                
                # Создаем разные размеры
                for size_name, dimensions in self.image_sizes.items():
                    size_dir = output_dir / size_name
                    size_dir.mkdir(exist_ok=True)
                    
                    resized = img.copy()
                    resized.thumbnail(dimensions, Image.Resampling.LANCZOS)
                    resized.save(size_dir / image_path.name, optimize=True, quality=85)
                    
        except Exception as e:
            print(f"Ошибка при обработке изображения {image_path}: {e}")
    
    def _copy_other_files(self) -> None:
        """Копирует остальные статические файлы."""
        for file_path in self.source_dir.rglob('*'):
            if file_path.is_file() and file_path not in self.processed_files:
                rel_path = file_path.relative_to(self.source_dir)
                output_path = self.output_dir / rel_path
                output_path.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(file_path, output_path)
    
    def get_asset_url(self, path: str, size: Optional[str] = None) -> str:
        """Получает URL для статического ресурса."""
        if size and size in self.image_sizes:
            return f"/static/{size}/{path}"
        return f"/static/{path}"
    
    def clear(self) -> None:
        """Очищает выходную директорию."""
        if self.output_dir.exists():
            shutil.rmtree(self.output_dir)
        self.processed_files.clear() 