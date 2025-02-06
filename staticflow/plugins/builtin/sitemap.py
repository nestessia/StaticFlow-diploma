from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from xml.etree import ElementTree as ET
from ..core.base import Plugin, PluginMetadata, HookType


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
            loc.text = f"{self.config['base_url'].rstrip('/')}/{page['url'].lstrip('/')}"
            
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
    
    def _save_sitemap(self, sitemap: ET.Element) -> None:
        """Сохраняет sitemap.xml."""
        output_path = Path(self.config['output_path']) / 'sitemap.xml'
        
        # Создаем директорию если её нет
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        tree = ET.ElementTree(sitemap)
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            method='xml'
        ) 