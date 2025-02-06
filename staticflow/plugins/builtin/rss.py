from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from xml.etree import ElementTree as ET
from ..core.base import Plugin, PluginMetadata, HookType


class RSSPlugin(Plugin):
    """Плагин для генерации RSS-ленты."""
    
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="rss",
            version="1.0.0",
            description="Генератор RSS-ленты",
            author="StaticFlow",
            requires_config=True
        )
    
    def validate_config(self) -> bool:
        """Проверяет конфигурацию плагина."""
        required = {
            'site_name',
            'site_description',
            'base_url',
            'output_path',
            'language'
        }
        return all(key in self.config for key in required)
    
    def on_post_build(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Генерирует RSS-ленту после сборки сайта."""
        pages = context.get('pages', [])
        if not pages:
            return context
            
        # Фильтруем только страницы с датой публикации
        pages = [p for p in pages if 'date' in p]
        # Сортируем по дате (новые первыми)
        pages.sort(key=lambda x: x['date'], reverse=True)
        
        rss = self._create_rss(pages[:10])  # Берем только 10 последних записей
        self._save_rss(rss)
        
        return context
    
    def _create_rss(self, pages: List[Dict[str, Any]]) -> ET.Element:
        """Создает XML структуру RSS."""
        # Создаем корневой элемент
        rss = ET.Element('rss', {'version': '2.0'})
        channel = ET.SubElement(rss, 'channel')
        
        # Добавляем информацию о канале
        title = ET.SubElement(channel, 'title')
        title.text = self.config['site_name']
        
        description = ET.SubElement(channel, 'description')
        description.text = self.config['site_description']
        
        link = ET.SubElement(channel, 'link')
        link.text = self.config['base_url']
        
        language = ET.SubElement(channel, 'language')
        language.text = self.config['language']
        
        generator = ET.SubElement(channel, 'generator')
        generator.text = 'StaticFlow RSS Generator'
        
        last_build = ET.SubElement(channel, 'lastBuildDate')
        last_build.text = datetime.now().strftime('%a, %d %b %Y %H:%M:%S %z')
        
        # Добавляем элементы
        for page in pages:
            item = ET.SubElement(channel, 'item')
            
            # Заголовок
            item_title = ET.SubElement(item, 'title')
            item_title.text = page.get('title', '')
            
            # Ссылка
            item_link = ET.SubElement(item, 'link')
            item_link.text = f"{self.config['base_url'].rstrip('/')}/{page['url'].lstrip('/')}"
            
            # Описание
            item_desc = ET.SubElement(item, 'description')
            item_desc.text = page.get('description', '')
            
            # Дата публикации
            if 'date' in page:
                pub_date = ET.SubElement(item, 'pubDate')
                pub_date.text = page['date'].strftime('%a, %d %b %Y %H:%M:%S %z')
            
            # GUID
            guid = ET.SubElement(item, 'guid')
            guid.text = f"{self.config['base_url'].rstrip('/')}/{page['url'].lstrip('/')}"
            
            # Автор
            if 'author' in page:
                author = ET.SubElement(item, 'author')
                author.text = page['author']
                
            # Категории
            if 'tags' in page:
                for tag in page['tags']:
                    category = ET.SubElement(item, 'category')
                    category.text = tag
                    
        return rss
    
    def _save_rss(self, rss: ET.Element) -> None:
        """Сохраняет RSS-ленту."""
        output_path = Path(self.config['output_path']) / 'feed.xml'
        
        # Создаем директорию если её нет
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Записываем файл
        tree = ET.ElementTree(rss)
        tree.write(
            output_path,
            encoding='utf-8',
            xml_declaration=True,
            method='xml'
        ) 