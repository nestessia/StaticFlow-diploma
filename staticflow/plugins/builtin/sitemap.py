from pathlib import Path
from typing import Dict, Any, List
from xml.etree import ElementTree as ET
from ..core.base import Plugin, PluginMetadata


class SitemapPlugin(Plugin):
    """Плагин для генерации Sitemap."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="sitemap",
            version="1.0.0",
            description="Генератор Sitemap",
            author="StaticFlow",
            requires_config=True
        )
    
    def process_content(self, content: str) -> str:
        """Пустая реализация для совместимости с интерфейсом плагина.
        Sitemap плагин не изменяет контент на этом этапе."""
        return content
    
    def validate_config(self) -> bool:
        """Проверяет конфигурацию плагина."""
        required = {'base_url', 'output_path'}
        return all(key in self.config for key in required)
    
    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует sitemap.xml после сборки сайта."""
        pages = context.get('pages', [])
        if not pages:
            return context
            
        sitemap = self._create_sitemap(pages)
        self._save_sitemap(sitemap)
        
        return context
    
    def _create_sitemap(self, pages: List[Dict[str, Any]]) -> ET.Element:
        """Создает XML структуру sitemap."""
        # Создаем корневой элемент
        urlset = ET.Element('urlset', {
            'xmlns': 'http://www.sitemaps.org/schemas/sitemap/0.9',
            'xmlns:xsi': 'http://www.w3.org/2001/XMLSchema-instance',
            'xsi:schemaLocation': (
                'http://www.sitemaps.org/schemas/sitemap/0.9 '
                'http://www.sitemaps.org/schemas/sitemap/0.9/sitemap.xsd'
            )
        })
        
        # Добавляем страницы
        for page in pages:
            url = ET.SubElement(urlset, 'url')
            
            # Обязательный тег loc
            loc = ET.SubElement(url, 'loc')
            base_url = self.config['base_url']
            if isinstance(base_url, Path):
                base_url = str(base_url)
            else:
                base_url = str(base_url)  # Всегда преобразуем к строке
                
            # Ensure page['url'] is a string before calling lstrip
            page_url = page['url']
            if isinstance(page_url, Path):
                page_url = str(page_url)
            else:
                page_url = str(page_url)  # Всегда преобразуем к строке
                
            # Теперь оба значения точно строки
            base_url_str = base_url.rstrip('/')
            page_url_str = page_url.lstrip('/')
            loc.text = f"{base_url_str}/{page_url_str}"
            
            # Дата последнего изменения
            if 'modified_at' in page:
                lastmod = ET.SubElement(url, 'lastmod')
                lastmod.text = page['modified_at'].strftime('%Y-%m-%d')
            
            # Частота изменения
            if 'change_freq' in page:
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = page['change_freq']
            
            # Приоритет
            if 'priority' in page:
                priority = ET.SubElement(url, 'priority')
                priority.text = str(page['priority'])
                
        return urlset
    
    def _save_sitemap(self, root: ET.Element) -> None:
        """Сохраняет файл карты сайта."""
        output_path_str = self.config['output_path']
        
        # Преобразуем к Path только если это строка
        if not isinstance(output_path_str, Path):
            output_dir = Path(output_path_str)
        else:
            output_dir = output_path_str
            
        output_path = output_dir / 'sitemap.xml'
        
        # Создаем директорию если её нет
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        tree = ET.ElementTree(root)
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            method='xml'
        ) 