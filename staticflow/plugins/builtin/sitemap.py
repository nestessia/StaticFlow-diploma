from pathlib import Path
from typing import Dict, Any, List
from xml.etree import ElementTree as ET
from ..core.base import Plugin, PluginMetadata
from ...utils.logging import get_logger

logger = get_logger("plugins.sitemap")

class SitemapPlugin(Plugin):
    """Плагин для генерации Sitemap."""
    
    def __init__(self):
        super().__init__({})
        logger.info("Sitemap plugin initialized")
    
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
        is_valid = all(key in self.config for key in required)
        if not is_valid:
            logger.error(f"Sitemap plugin config validation failed. Required keys: {required}")
        return is_valid
    
    def post_build(self, site) -> None:
        """Генерирует sitemap.xml после сборки сайта."""
        logger.info("Sitemap plugin: post_build called")
        
        if not self.validate_config():
            logger.error("Sitemap plugin: invalid configuration")
            return
            
        pages = site.get_all_pages()
        if not pages:
            logger.warning("Sitemap plugin: no pages found")
            return
            
        logger.info(f"Sitemap plugin: found {len(pages)} pages")
        
        try:
            sitemap = self._create_sitemap(pages)
            self._save_sitemap(sitemap)
            logger.info("Sitemap plugin: sitemap.xml generated successfully")
        except Exception as e:
            logger.error(f"Sitemap plugin: error generating sitemap: {str(e)}")
    
    def _create_sitemap(self, pages: List[Dict[str, Any]]) -> ET.Element:
        """Создает XML структуру sitemap."""
        logger.info("Sitemap plugin: creating sitemap structure")
        
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
            page_url = page.url if hasattr(page, 'url') else page.get('url')
            if not page_url:
                logger.warning(f"Sitemap plugin: page has no URL: {page}")
                continue
                
            if isinstance(page_url, Path):
                page_url = str(page_url)
            else:
                page_url = str(page_url)  # Всегда преобразуем к строке
                
            # Теперь оба значения точно строки
            base_url_str = base_url.rstrip('/')
            page_url_str = page_url.lstrip('/')
            loc.text = f"{base_url_str}/{page_url_str}"
            
            # Дата последнего изменения
            if hasattr(page, 'modified_at'):
                lastmod = ET.SubElement(url, 'lastmod')
                lastmod.text = page.modified_at.strftime('%Y-%m-%d')
            elif 'modified_at' in page:
                lastmod = ET.SubElement(url, 'lastmod')
                lastmod.text = page['modified_at'].strftime('%Y-%m-%d')
            
            # Частота изменения
            if hasattr(page, 'change_freq'):
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = page.change_freq
            elif 'change_freq' in page:
                changefreq = ET.SubElement(url, 'changefreq')
                changefreq.text = page['change_freq']
            
            # Приоритет
            if hasattr(page, 'priority'):
                priority = ET.SubElement(url, 'priority')
                priority.text = str(page.priority)
            elif 'priority' in page:
                priority = ET.SubElement(url, 'priority')
                priority.text = str(page['priority'])
                
        return urlset
    
    def _save_sitemap(self, root: ET.Element) -> None:
        """Сохраняет файл карты сайта."""
        output_path_str = self.config['output_path']
        logger.info(f"Sitemap plugin: saving sitemap to {output_path_str}")
        
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
        logger.info(f"Sitemap plugin: sitemap.xml saved to {output_path}") 